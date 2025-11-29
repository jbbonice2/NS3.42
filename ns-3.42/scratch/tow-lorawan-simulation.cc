#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lorawan-module.h"
#include "ns3/applications-module.h"
#include "ns3/internet-module.h"
#include "ns3/random-variable-stream.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE("TowLoRaWANChannelSelection");

// Structure pour stocker les statistiques
struct TransmissionStats {
    uint32_t successful = 0;
    uint32_t attempted = 0;
    std::map<uint32_t, uint32_t> successfulPerChannel;
    std::map<uint32_t, uint32_t> attemptedPerChannel;
};

// Classe pour l'algorithme ToW
class TowChannelSelector {
private:
    uint32_t m_numChannels;
    std::vector<double> m_qValues;
    std::vector<uint32_t> m_nCount;
    std::vector<uint32_t> m_rCount;
    std::vector<double> m_rewardProb;
    uint32_t m_timeStep;
    double m_alpha;      // Discount factor
    double m_beta;       // Forgetting factor
    double m_amplitude;  // Oscillation amplitude
    Ptr<UniformRandomVariable> m_random;
    
public:
    TowChannelSelector(uint32_t numChannels, double alpha = 0.9, double beta = 0.9, double amplitude = 0.5)
        : m_numChannels(numChannels), m_alpha(alpha), m_beta(beta), m_amplitude(amplitude), m_timeStep(0)
    {
        m_qValues.resize(numChannels, 0.0);
        m_nCount.resize(numChannels, 0);
        m_rCount.resize(numChannels, 0);
        m_rewardProb.resize(numChannels, 0.0);
        m_random = CreateObject<UniformRandomVariable>();
    }
    
    uint32_t SelectChannel() {
        if (m_timeStep == 0) {
            // Random selection for first decision
            return m_random->GetInteger(0, m_numChannels - 1);
        }
        
        std::vector<double> xValues(m_numChannels);
        for (uint32_t k = 0; k < m_numChannels; k++) {
            // Calculate average Q value of other channels
            double avgOthers = 0.0;
            for (uint32_t j = 0; j < m_numChannels; j++) {
                if (j != k) avgOthers += m_qValues[j];
            }
            avgOthers /= (m_numChannels - 1);
            
            // Calculate oscillation component
            double osc = m_amplitude * cos(2.0 * M_PI * (m_timeStep + k) / m_numChannels);
            
            // Calculate X_k(t) according to Eq. (6)
            xValues[k] = m_qValues[k] - avgOthers + osc;
        }
        
        // Select channel with maximum X_k(t)
        auto maxIt = std::max_element(xValues.begin(), xValues.end());
        uint32_t selectedChannel = std::distance(xValues.begin(), maxIt);
        
        // Handle ties randomly
        std::vector<uint32_t> maxChannels;
        double maxValue = *maxIt;
        for (uint32_t k = 0; k < m_numChannels; k++) {
            if (std::abs(xValues[k] - maxValue) < 1e-9) {
                maxChannels.push_back(k);
            }
        }
        
        if (maxChannels.size() > 1) {
            selectedChannel = maxChannels[m_random->GetInteger(0, maxChannels.size() - 1)];
        }
        
        return selectedChannel;
    }
    
    void UpdateReward(uint32_t channel, bool success) {
        m_timeStep++;
        
        // Update N_k(t) and R_k(t) according to Eq. (12) and (13)
        for (uint32_t k = 0; k < m_numChannels; k++) {
            if (k == channel) {
                m_nCount[k] = 1 + m_beta * m_nCount[k];
                if (success) {
                    m_rCount[k] = 1 + m_beta * m_rCount[k];
                } else {
                    m_rCount[k] = m_beta * m_rCount[k];
                }
            } else {
                m_nCount[k] = m_beta * m_nCount[k];
                m_rCount[k] = m_beta * m_rCount[k];
            }
        }
        
        // Update reward probabilities
        for (uint32_t k = 0; k < m_numChannels; k++) {
            if (m_nCount[k] > 0) {
                m_rewardProb[k] = m_rCount[k] / m_nCount[k];
            }
        }
        
        // Calculate delta Q according to Eq. (9)
        double deltaQ;
        if (success) {
            deltaQ = 1.0;
        } else {
            // Calculate omega(t) according to Eq. (10)
            std::vector<double> sortedProbs = m_rewardProb;
            std::sort(sortedProbs.rbegin(), sortedProbs.rend());
            double p1st = sortedProbs.size() > 0 ? sortedProbs[0] : 0.0;
            double p2nd = sortedProbs.size() > 1 ? sortedProbs[1] : 0.0;
            double omega = (p1st + p2nd) / 2.0 - std::abs(p1st - p2nd);
            deltaQ = -omega;
        }
        
        // Update Q value according to Eq. (8)
        m_qValues[channel] = m_alpha * m_qValues[channel] + deltaQ;
        
        // Update other Q values with discount only
        for (uint32_t k = 0; k < m_numChannels; k++) {
            if (k != channel) {
                m_qValues[k] = m_alpha * m_qValues[k];
            }
        }
    }
};

// Classe pour UCB1-Tuned
class UCB1TunedChannelSelector {
private:
    uint32_t m_numChannels;
    std::vector<double> m_empiricalMean;
    std::vector<double> m_empiricalVariance;
    std::vector<uint32_t> m_nCount;
    std::vector<double> m_sumRewards;
    std::vector<double> m_sumSquaredRewards;
    uint32_t m_totalTime;
    Ptr<UniformRandomVariable> m_random;
    
public:
    UCB1TunedChannelSelector(uint32_t numChannels) 
        : m_numChannels(numChannels), m_totalTime(0)
    {
        m_empiricalMean.resize(numChannels, 0.0);
        m_empiricalVariance.resize(numChannels, 0.0);
        m_nCount.resize(numChannels, 0);
        m_sumRewards.resize(numChannels, 0.0);
        m_sumSquaredRewards.resize(numChannels, 0.0);
        m_random = CreateObject<UniformRandomVariable>();
    }
    
    uint32_t SelectChannel() {
        m_totalTime++;
        
        // Play each channel at least once
        for (uint32_t k = 0; k < m_numChannels; k++) {
            if (m_nCount[k] == 0) {
                return k;
            }
        }
        
        std::vector<double> ucbValues(m_numChannels);
        for (uint32_t k = 0; k < m_numChannels; k++) {
            double variance = m_empiricalVariance[k] + std::sqrt(2.0 * std::log(m_totalTime) / m_nCount[k]);
            double confidence = std::sqrt(std::log(m_totalTime) / m_nCount[k] * std::min(0.25, variance));
            ucbValues[k] = m_empiricalMean[k] + confidence;
        }
        
        auto maxIt = std::max_element(ucbValues.begin(), ucbValues.end());
        return std::distance(ucbValues.begin(), maxIt);
    }
    
    void UpdateReward(uint32_t channel, bool success) {
        double reward = success ? 1.0 : 0.0;
        m_nCount[channel]++;
        m_sumRewards[channel] += reward;
        m_sumSquaredRewards[channel] += reward * reward;
        
        // Update empirical mean
        m_empiricalMean[channel] = m_sumRewards[channel] / m_nCount[channel];
        
        // Update empirical variance
        if (m_nCount[channel] > 1) {
            double meanSquared = m_empiricalMean[channel] * m_empiricalMean[channel];
            double secondMoment = m_sumSquaredRewards[channel] / m_nCount[channel];
            m_empiricalVariance[channel] = secondMoment - meanSquared;
        }
    }
};

// Classe pour ε-greedy
class EpsilonGreedyChannelSelector {
private:
    uint32_t m_numChannels;
    std::vector<double> m_rewardProb;
    std::vector<uint32_t> m_nCount;
    std::vector<uint32_t> m_rCount;
    double m_epsilon;
    Ptr<UniformRandomVariable> m_random;
    
public:
    EpsilonGreedyChannelSelector(uint32_t numChannels, double epsilon = 0.1)
        : m_numChannels(numChannels), m_epsilon(epsilon)
    {
        m_rewardProb.resize(numChannels, 0.0);
        m_nCount.resize(numChannels, 0);
        m_rCount.resize(numChannels, 0);
        m_random = CreateObject<UniformRandomVariable>();
    }
    
    uint32_t SelectChannel() {
        if (m_random->GetValue() < m_epsilon) {
            // Exploration: random selection
            return m_random->GetInteger(0, m_numChannels - 1);
        } else {
            // Exploitation: select best channel
            auto maxIt = std::max_element(m_rewardProb.begin(), m_rewardProb.end());
            return std::distance(m_rewardProb.begin(), maxIt);
        }
    }
    
    void UpdateReward(uint32_t channel, bool success) {
        m_nCount[channel]++;
        if (success) {
            m_rCount[channel]++;
        }
        
        if (m_nCount[channel] > 0) {
            m_rewardProb[channel] = (double)m_rCount[channel] / m_nCount[channel];
        }
    }
};

// Classe pour sélection aléatoire
class RandomChannelSelector {
private:
    uint32_t m_numChannels;
    Ptr<UniformRandomVariable> m_random;
    
public:
    RandomChannelSelector(uint32_t numChannels) : m_numChannels(numChannels)
    {
        m_random = CreateObject<UniformRandomVariable>();
    }
    
    uint32_t SelectChannel() {
        return m_random->GetInteger(0, m_numChannels - 1);
    }
    
    void UpdateReward(uint32_t channel, bool success) {
        // No learning for random selection
    }
};

// Application personnalisée pour LoRa End Device avec sélection de canal
class LoRaEndDeviceApplication : public Application {
private:
    Ptr<LoraNetDevice> m_netDevice;
    Time m_interval;
    uint32_t m_packetSize;
    uint32_t m_maxRetransmissions;
    EventId m_sendEvent;
    uint32_t m_sent;
    uint32_t m_received;
    TransmissionStats* m_stats;
    
    // Channel selectors
    TowChannelSelector* m_towSelector;
    UCB1TunedChannelSelector* m_ucb1Selector;
    EpsilonGreedyChannelSelector* m_epsilonSelector;
    RandomChannelSelector* m_randomSelector;
    
    std::string m_algorithm;
    uint32_t m_lastSelectedChannel;
    bool m_waitingForAck;
    EventId m_ackTimeoutEvent;
    
    std::vector<uint32_t> m_availableChannels;
    uint32_t m_currentTime; // Minutes depuis le début
    
public:
    LoRaEndDeviceApplication() 
        : m_interval(Seconds(10)), m_packetSize(50), m_maxRetransmissions(3),
          m_sent(0), m_received(0), m_stats(nullptr),
          m_towSelector(nullptr), m_ucb1Selector(nullptr), 
          m_epsilonSelector(nullptr), m_randomSelector(nullptr),
          m_waitingForAck(false), m_currentTime(0)
    {
        // Channels that end devices can access: CH1, CH3, CH5, CH7, CH9 (0, 2, 4, 6, 8)
        m_availableChannels = {0, 2, 4, 6, 8};
    }
    
    void SetTransmissionStats(TransmissionStats* stats) { m_stats = stats; }
    void SetInterval(Time interval) { m_interval = interval; }
    void SetPacketSize(uint32_t size) { m_packetSize = size; }
    void SetMaxRetransmissions(uint32_t max) { m_maxRetransmissions = max; }
    void SetAlgorithm(const std::string& algorithm) { m_algorithm = algorithm; }
    
    void SetChannelSelectors(TowChannelSelector* tow, UCB1TunedChannelSelector* ucb1,
                           EpsilonGreedyChannelSelector* epsilon, RandomChannelSelector* random) {
        m_towSelector = tow;
        m_ucb1Selector = ucb1;
        m_epsilonSelector = epsilon;
        m_randomSelector = random;
    }
    
    void UpdateCurrentTime(uint32_t timeMinutes) {
        m_currentTime = timeMinutes;
    }
    
    bool IsChannelAvailable(uint32_t channel) {
        // Scenario 2: Dynamic channel availability
        if (m_currentTime < 10) {
            // 0-10 min: CH1, CH3, CH5 available (channels 0, 2, 4)
            return (channel == 0 || channel == 2 || channel == 4);
        } else if (m_currentTime < 20) {
            // 10-20 min: CH1, CH3 available (channels 0, 2)
            return (channel == 0 || channel == 2);
        } else if (m_currentTime < 30) {
            // 20-30 min: CH3, CH5 available (channels 2, 4)
            return (channel == 2 || channel == 4);
        } else if (m_currentTime < 40) {
            // 30-40 min: CH1, CH5 available (channels 0, 4)
            return (channel == 0 || channel == 4);
        }
        // Default: all channels available
        return (channel == 0 || channel == 2 || channel == 4);
    }
    
    uint32_t SelectChannel() {
        uint32_t selectedChannel;
        
        if (m_algorithm == "ToW") {
            selectedChannel = m_towSelector->SelectChannel();
        } else if (m_algorithm == "UCB1-Tuned") {
            selectedChannel = m_ucb1Selector->SelectChannel();
        } else if (m_algorithm == "EpsilonGreedy") {
            selectedChannel = m_epsilonSelector->SelectChannel();
        } else { // Random
            selectedChannel = m_randomSelector->SelectChannel();
        }
        
        return selectedChannel;
    }
    
    void UpdateChannelSelector(uint32_t channel, bool success) {
        if (m_algorithm == "ToW") {
            m_towSelector->UpdateReward(channel, success);
        } else if (m_algorithm == "UCB1-Tuned") {
            m_ucb1Selector->UpdateReward(channel, success);
        } else if (m_algorithm == "EpsilonGreedy") {
            m_epsilonSelector->UpdateReward(channel, success);
        } else { // Random
            m_randomSelector->UpdateReward(channel, success);
        }
    }

protected:
    virtual void StartApplication() override {
        m_netDevice = GetNode()->GetDevice(0)->GetObject<LoraNetDevice>();
        ScheduleNextTransmission();
    }
    
    virtual void StopApplication() override {
        if (m_sendEvent.IsRunning()) {
            Simulator::Cancel(m_sendEvent);
        }
        if (m_ackTimeoutEvent.IsRunning()) {
            Simulator::Cancel(m_ackTimeoutEvent);
        }
    }
    
private:
    void ScheduleNextTransmission() {
        m_sendEvent = Simulator::Schedule(m_interval, &LoRaEndDeviceApplication::SendPacket, this);
    }
    
    void SendPacket() {
        if (!m_waitingForAck) {
            // Select channel using the chosen algorithm
            m_lastSelectedChannel = SelectChannel();
            
            // Map logical channel to actual LoRaWAN channel
            uint32_t actualChannel = m_availableChannels[m_lastSelectedChannel];
            
            // Set the channel in the LoRa PHY layer
            Ptr<LoraNetDevice> netDevice = GetNode()->GetDevice(0)->GetObject<LoraNetDevice>();
            Ptr<LoraPhy> phy = netDevice->GetPhy();
            phy->GetObject<EndDeviceLoraPhy>()->SetFrequency(868.1e6 + actualChannel * 0.2e6);
            
            // Create and send packet
            Ptr<Packet> packet = Create<Packet>(m_packetSize);
            
            // Add custom header to identify the packet
            LoraTag tag;
            tag.SetSpreadingFactor(7);
            tag.SetDataRate(5);
            packet->AddPacketTag(tag);
            
            // Send the packet
            bool sent = m_netDevice->Send(packet, m_netDevice->GetBroadcast(), 0x0800);
            
            if (sent) {
                m_sent++;
                if (m_stats) {
                    m_stats->attempted++;
                    m_stats->attemptedPerChannel[actualChannel]++;
                }
                
                m_waitingForAck = true;
                
                // Schedule ACK timeout (simulated - in real LoRaWAN this would be handled by MAC layer)
                m_ackTimeoutEvent = Simulator::Schedule(Seconds(5), &LoRaEndDeviceApplication::OnAckTimeout, this);
                
                // Simulate ACK reception based on channel availability
                bool channelAvailable = IsChannelAvailable(actualChannel);
                if (channelAvailable) {
                    // High probability of success on available channels
                    Ptr<UniformRandomVariable> random = CreateObject<UniformRandomVariable>();
                    if (random->GetValue() < 0.9) { // 90% success rate on available channels
                        Simulator::Schedule(Seconds(2), &LoRaEndDeviceApplication::OnAckReceived, this);
                    }
                } else {
                    // Low probability of success on unavailable channels
                    Ptr<UniformRandomVariable> random = CreateObject<UniformRandomVariable>();
                    if (random->GetValue() < 0.1) { // 10% success rate on unavailable channels
                        Simulator::Schedule(Seconds(2), &LoRaEndDeviceApplication::OnAckReceived, this);
                    }
                }
            }
        }
        
        ScheduleNextTransmission();
    }
    
    void OnAckReceived() {
        if (m_waitingForAck) {
            m_received++;
            if (m_stats) {
                m_stats->successful++;
                uint32_t actualChannel = m_availableChannels[m_lastSelectedChannel];
                m_stats->successfulPerChannel[actualChannel]++;
            }
            
            // Update channel selector with positive reward
            UpdateChannelSelector(m_lastSelectedChannel, true);
            
            m_waitingForAck = false;
            if (m_ackTimeoutEvent.IsRunning()) {
                Simulator::Cancel(m_ackTimeoutEvent);
            }
        }
    }
    
    void OnAckTimeout() {
        if (m_waitingForAck) {
            // Update channel selector with negative reward
            UpdateChannelSelector(m_lastSelectedChannel, false);
            m_waitingForAck = false;
        }
    }
};

// Fonction pour créer les dispositifs LoRa
void SetupLoRaWANNetwork(NodeContainer& endDevices, NodeContainer& gateways,
                        NetDeviceContainer& endDevicesNetDevices, NetDeviceContainer& gatewayNetDevices) {
    // Create the LoRa channel
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(3.76);
    loss->SetReference(1, 7.7);

    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();

    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

    // Create the LoRaWAN helper
    LoraPhyHelper phyHelper = LoraPhyHelper();
    phyHelper.SetChannel(channel);

    // Create a MAC layer helper
    LorawanMacHelper macHelper = LorawanMacHelper();

    // Create a helper to create LoRa NetDevices
    LoraHelper helper = LoraHelper();
    helper.EnablePacketTracking();

    // Create end devices
    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    helper.Install(phyHelper, macHelper, endDevices);
    endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

    // Create gateways
    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    gatewayNetDevices = helper.Install(phyHelper, macHelper, gateways);
}

// Fonction principale pour le scénario 1
void RunScenario1(const std::string& algorithm, uint32_t numDevices, double& fsr) {
    NodeContainer endDevices;
    NodeContainer gateways;
    endDevices.Create(numDevices);
    gateways.Create(1);

    // Position the nodes
    MobilityHelper mobility;
    Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
    
    // Gateway at center
    allocator->Add(Vector(0.0, 0.0, 0.0));
    
    // End devices in a circle around gateway
    for (uint32_t i = 0; i < numDevices; i++) {
        double angle = 2.0 * M_PI * i / numDevices;
        double radius = 1000.0; // 1 km radius
        allocator->Add(Vector(radius * cos(angle), radius * sin(angle), 0.0));
    }
    
    mobility.SetPositionAllocator(allocator);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(endDevices);
    mobility.Install(gateways);

    NetDeviceContainer endDevicesNetDevices;
    NetDeviceContainer gatewayNetDevices;
    SetupLoRaWANNetwork(endDevices, gateways, endDevicesNetDevices, gatewayNetDevices);

    // Create channel selectors (5 logical channels)
    TowChannelSelector towSelector(5);
    UCB1TunedChannelSelector ucb1Selector(5);
    EpsilonGreedyChannelSelector epsilonSelector(5);
    RandomChannelSelector randomSelector(5);

    // Install applications on end devices
    TransmissionStats stats;
    
    for (uint32_t i = 0; i < numDevices; i++) {
        Ptr<LoRaEndDeviceApplication> app = CreateObject<LoRaEndDeviceApplication>();
        app->SetTransmissionStats(&stats);
        app->SetAlgorithm(algorithm);
        app->SetChannelSelectors(&towSelector, &ucb1Selector, &epsilonSelector, &randomSelector);
        endDevices.Get(i)->AddApplication(app);
        app->SetStartTime(Seconds(1));
        app->SetStopTime(Minutes(30)); // 30 minutes simulation
    }

    // Run simulation
    Simulator::Stop(Minutes(30));
    Simulator::Run();
    Simulator::Destroy();

    // Calculate FSR
    fsr = (stats.attempted > 0) ? (double)stats.successful / stats.attempted : 0.0;
}

// Fonction pour le scénario 2
void RunScenario2(const std::string& algorithm, 
                 std::map<uint32_t, uint32_t>& successfulPerChannel,
                 double& avgFsr) {
    
    const uint32_t numDevices = 30;
    NodeContainer endDevices;
    NodeContainer gateways;
    endDevices.Create(numDevices);
    gateways.Create(1);

    // Position the nodes
    MobilityHelper mobility;
    Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
    
    // Gateway at center
    allocator->Add(Vector(0.0, 0.0, 0.0));
    
    // End devices in a circle around gateway
    for (uint32_t i = 0; i < numDevices; i++) {
        double angle = 2.0 * M_PI * i / numDevices;
        double radius = 1000.0;
        allocator->Add(Vector(radius * cos(angle), radius * sin(angle), 0.0));
    }
    
    mobility.SetPositionAllocator(allocator);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(endDevices);
    mobility.Install(gateways);

    NetDeviceContainer endDevicesNetDevices;
    NetDeviceContainer gatewayNetDevices;
    SetupLoRaWANNetwork(endDevices, gateways, endDevicesNetDevices, gatewayNetDevices);

    // Create channel selectors
    TowChannelSelector towSelector(5);
    UCB1TunedChannelSelector ucb1Selector(5);
    EpsilonGreedyChannelSelector epsilonSelector(5);
    RandomChannelSelector randomSelector(5);

    // Install applications on end devices
    TransmissionStats stats;
    std::vector<Ptr<LoRaEndDeviceApplication>> apps;
    
    for (uint32_t i = 0; i < numDevices; i++) {
        Ptr<LoRaEndDeviceApplication> app = CreateObject<LoRaEndDeviceApplication>();
        app->SetTransmissionStats(&stats);
        app->SetAlgorithm(algorithm);
        app->SetChannelSelectors(&towSelector, &ucb1Selector, &epsilonSelector, &randomSelector);
        apps.push_back(app);
        endDevices.Get(i)->AddApplication(app);
        app->SetStartTime(Seconds(1));
        app->SetStopTime(Minutes(40));
    }

    // Schedule time updates for dynamic channel availability
    for (uint32_t t = 0; t < 40; t++) {
        Simulator::Schedule(Minutes(t), [&apps, t]() {
            for (auto app : apps) {
                app->UpdateCurrentTime(t);
            }
        });
    }

    // Run simulation
    Simulator::Stop(Minutes(40));
    Simulator::Run();
    
    successfulPerChannel = stats.successfulPerChannel;
    avgFsr = (stats.attempted > 0) ? (double)stats.successful / stats.attempted : 0.0;
    
    Simulator::Destroy();
}

int main(int argc, char* argv[]) {
    CommandLine cmd;
    std::string scenario = "1";
    std::string algorithm = "ToW";
    uint32_t numDevices = 10;
    
    cmd.AddValue("scenario", "Scenario to run (1 or 2)", scenario);
    cmd.AddValue("algorithm", "Algorithm to use (ToW, UCB1-Tuned, EpsilonGreedy, Random)", algorithm);
    cmd.AddValue("numDevices", "Number of end devices", numDevices);
    cmd.Parse(argc, argv);

    LogComponentEnable("TowLoRaWANChannelSelection", LOG_LEVEL_INFO);

    if (scenario == "1") {
        // Scenario 1: FSR vs number of devices
        std::ofstream outFile("scenario1_" + algorithm + ".txt");
        
        for (uint32_t n = 2; n <= 30; n += 2) {
            double fsr;
            RunScenario1(algorithm, n, fsr);
            outFile << n << " " << fsr << std::endl;
            std::cout << "Devices: " << n << ", FSR: " << fsr << std::endl;
        }
        outFile.close();
        
    } else if (scenario == "2") {
        // Scenario 2: Dynamic channels
        std::map<uint32_t, uint32_t> successfulPerChannel;
        double avgFsr;
        
        RunScenario2(algorithm, successfulPerChannel, avgFsr);
        
        std::ofstream outFile("scenario2_" + algorithm + ".txt");
        outFile << "Average FSR: " << avgFsr << std::endl;
        
        // Output successful transmissions per channel
        for (auto& pair : successfulPerChannel) {
            outFile << "Channel " << pair.first << ": " << pair.second << " successful transmissions" << std::endl;
        }
        outFile.close();
        
        std::cout << "Algorithm: " << algorithm << ", Average FSR: " << avgFsr << std::endl;
    }

    return 0;
}