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
#include <ctime>  // Pour timestamps dans logs

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE("TowLoRaWANChannelSelection");

// Structure pour stocker les statistiques, avec traces temporelles
struct TransmissionStats {
    uint32_t successful = 0;
    uint32_t attempted = 0;
    std::map<uint32_t, uint32_t> successfulPerChannel;
    std::map<uint32_t, uint32_t> attemptedPerChannel;
    std::map<uint32_t, std::map<uint32_t, uint32_t>> successfulPerChannelPerMinute;  // Minute -> Channel -> Success
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
        : m_numChannels(numChannels), m_timeStep(0), m_alpha(alpha), m_beta(beta), m_amplitude(amplitude)
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

// ... (UCB1TunedChannelSelector, EpsilonGreedyChannelSelector, RandomChannelSelector remain unchanged)

// LoRaEndDeviceApplication class (fixed)
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
        m_availableChannels = {0, 2, 4, 6, 8}; // CH1,3,5,7,9
    }
    
    ~LoRaEndDeviceApplication() {}
    
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
        if (m_currentTime < 10) return (channel == 0 || channel == 2 || channel == 4);
        else if (m_currentTime < 20) return (channel == 0 || channel == 2);
        else if (m_currentTime < 30) return (channel == 2 || channel == 4);
        else if (m_currentTime < 40) return (channel == 0 || channel == 4);
        return true;
    }
    
    uint32_t SelectChannel() {
        uint32_t selectedChannel;
        
        if (m_algorithm == "ToW") {
            selectedChannel = m_towSelector->SelectChannel();
        } else if (m_algorithm == "UCB1-Tuned") {
            selectedChannel = m_ucb1Selector->SelectChannel();
        } else if (m_algorithm == "EpsilonGreedy") {
            selectedChannel = m_epsilonSelector->SelectChannel();
        } else {
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
        } else {
            m_randomSelector->UpdateReward(channel, success);
        }
    }

protected:
    virtual void StartApplication() override {
        m_netDevice = GetNode()->GetDevice(0)->GetObject<LoraNetDevice>();
        ScheduleNextTransmission();
    }
    
    virtual void StopApplication() override {
        if (m_sendEvent.IsPending()) {
            Simulator::Cancel(m_sendEvent);
        }
        if (m_ackTimeoutEvent.IsPending()) {
            Simulator::Cancel(m_ackTimeoutEvent);
        }
    }
    
private:
    void ScheduleNextTransmission() {
        m_sendEvent = Simulator::Schedule(m_interval, &LoRaEndDeviceApplication::SendPacket, this);
    }
    
    void SendPacket() {
        if (!m_waitingForAck) {
            m_lastSelectedChannel = SelectChannel();
            uint32_t actualChannel = m_availableChannels[m_lastSelectedChannel];
            
            if (!IsChannelAvailable(actualChannel)) {
                UpdateChannelSelector(m_lastSelectedChannel, false);
                ScheduleNextTransmission();
                return;
            }
            
            Ptr<LoraPhy> phy = m_netDevice->GetPhy();
            Ptr<EndDeviceLoraPhy> edPhy = phy->GetObject<EndDeviceLoraPhy>();
            
            edPhy->SetFrequency(868.1e6 + actualChannel * 0.2e6); // Example frequencies
            
            if (phy->IsTransmitting() || edPhy->GetState() != EndDeviceLoraPhy::STANDBY) {
                UpdateChannelSelector(m_lastSelectedChannel, false);
                ScheduleNextTransmission();
                return;
            }
            
            Ptr<Packet> packet = Create<Packet>(m_packetSize);
            LoraTag tag;
            tag.SetSpreadingFactor(7);
            tag.SetDataRate(5);
            packet->AddPacketTag(tag);
            
            bool sent = m_netDevice->Send(packet, m_netDevice->GetBroadcast(), 0x0800);
            
            if (sent) {
                m_sent++;
                if (m_stats) {
                    m_stats->attempted++;
                    m_stats->attemptedPerChannel[actualChannel]++;
                }
                m_waitingForAck = true;
                m_ackTimeoutEvent = Simulator::Schedule(Seconds(1.0), &LoRaEndDeviceApplication::OnAckTimeout, this);
            }
        }
        ScheduleNextTransmission();
    }
    
    void OnPacketReceived(Ptr<const Packet> packet) {
        if (m_waitingForAck) {
            m_received++;
            uint32_t minute = static_cast<uint32_t>(Simulator::Now().GetMinutes());
            if (m_stats) {
                m_stats->successful++;
                uint32_t actualChannel = m_availableChannels[m_lastSelectedChannel];
                m_stats->successfulPerChannel[actualChannel]++;
                m_stats->successfulPerChannelPerMinute[minute][actualChannel]++;
            }
            UpdateChannelSelector(m_lastSelectedChannel, true);
            m_waitingForAck = false;
            if (m_ackTimeoutEvent.IsPending()) {
                Simulator::Cancel(m_ackTimeoutEvent);
            }
        }
    }
    
    void OnAckTimeout() {
        if (m_waitingForAck) {
            UpdateChannelSelector(m_lastSelectedChannel, false);
            m_waitingForAck = false;
        }
    }
};

// SetupLoRaWANNetwork (fixed: removed invalid interference set)
void SetupLoRaWANNetwork(NodeContainer& endDevices, NodeContainer& gateways,
                         NetDeviceContainer& endDevicesNetDevices, NetDeviceContainer& gatewayNetDevices) {
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(3.76);
    loss->SetReference(1, 7.7);

    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();

    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

    LoraPhyHelper phyHelper = LoraPhyHelper();
    phyHelper.SetChannel(channel);

    LorawanMacHelper macHelper = LorawanMacHelper();

    LoraHelper helper = LoraHelper();
    helper.EnablePacketTracking();

    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    gatewayNetDevices = helper.Install(phyHelper, macHelper, gateways);
    
    // Trace received packets
    for (uint32_t i = 0; i < endDevices.GetN(); ++i) {
        Ptr<LoRaEndDeviceApplication> app = DynamicCast<LoRaEndDeviceApplication>(endDevices.Get(i)->GetApplication(0));
        if (app) {
            app->m_netDevice->GetMac()->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&LoRaEndDeviceApplication::OnPacketReceived, app));
        }
    }
}

// RunScenario1 (unchanged)
void RunScenario1(const std::string& algorithm, uint32_t numDevices, double& fsr) {
    RngSeedManager::SetSeed(42);
    
    NodeContainer endDevices;
    NodeContainer gateways;
    endDevices.Create(numDevices);
    gateways.Create(1);

    MobilityHelper mobility;
    Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
    allocator->Add(Vector(0.0, 0.0, 0.0));
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

    TowChannelSelector towSelector(5);
    UCB1TunedChannelSelector ucb1Selector(5);
    EpsilonGreedyChannelSelector epsilonSelector(5);
    RandomChannelSelector randomSelector(5);

    TransmissionStats stats;
    
    for (uint32_t i = 0; i < numDevices; i++) {
        Ptr<LoRaEndDeviceApplication> app = CreateObject<LoRaEndDeviceApplication>();
        app->SetTransmissionStats(&stats);
        app->SetAlgorithm(algorithm);
        app->SetChannelSelectors(&towSelector, &ucb1Selector, &epsilonSelector, &randomSelector);
        endDevices.Get(i)->AddApplication(app);
        app->SetStartTime(Seconds(1));
        app->SetStopTime(Minutes(30));
    }

    Simulator::Stop(Minutes(30));
    Simulator::Run();
    Simulator::Destroy();

    fsr = (stats.attempted > 0) ? (double)stats.successful / stats.attempted : 0.0;
}

// RunScenario2 (removed invalid Add/Remove; dynamic handled on ED side)
void RunScenario2(const std::string& algorithm, 
                  std::map<uint32_t, uint32_t>& successfulPerChannel,
                  double& avgFsr) {
    RngSeedManager::SetSeed(42);
    const uint32_t numDevices = 30;
    NodeContainer endDevices;
    NodeContainer gateways;
    endDevices.Create(numDevices);
    gateways.Create(1);

    MobilityHelper mobility;
    Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
    allocator->Add(Vector(0.0, 0.0, 0.0));
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

    TowChannelSelector towSelector(5);
    UCB1TunedChannelSelector ucb1Selector(5);
    EpsilonGreedyChannelSelector epsilonSelector(5);
    RandomChannelSelector randomSelector(5);

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

    for (uint32_t t = 0; t < 40; t++) {
        Simulator::Schedule(Minutes(t), [&apps, t]() {
            for (auto app : apps) {
                app->UpdateCurrentTime(t);
            }
        });
    }

    Simulator::Stop(Minutes(40));
    Simulator::Run();
    
    successfulPerChannel = stats.successfulPerChannel;
    avgFsr = (stats.attempted > 0) ? (double)stats.successful / stats.attempted : 0.0;
    
    std::ofstream traceFile("scenario2_" + algorithm + "_traces.csv");
    traceFile << "Minute,Channel0,Channel2,Channel4,Channel6,Channel8\n";
    for (uint32_t min = 0; min < 40; ++min) {
        traceFile << min;
        for (auto ch : {0,2,4,6,8}) {
            traceFile << "," << stats.successfulPerChannelPerMinute[min][ch];
        }
        traceFile << "\n";
    }
    traceFile.close();
    
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
        std::ofstream outFile("scenario1_" + algorithm + ".txt");
        
        for (uint32_t n = 2; n <= 30; n += 2) {
            double fsr;
            RunScenario1(algorithm, n, fsr);
            outFile << n << " " << fsr << std::endl;
            std::cout << "Devices: " << n << ", FSR: " << fsr << std::endl;
        }
        outFile.close();
        
    } else if (scenario == "2") {
        std::map<uint32_t, uint32_t> successfulPerChannel;
        double avgFsr;
        
        RunScenario2(algorithm, successfulPerChannel, avgFsr);
        
        std::ofstream outFile("scenario2_" + algorithm + ".txt");
        outFile << "Average FSR: " << avgFsr << std::endl;
        
        for (auto& pair : successfulPerChannel) {
            outFile << "Channel " << pair.first << ": " << pair.second << " successful transmissions" << std::endl;
        }
        outFile.close();
        
        std::cout << "Algorithm: " << algorithm << ", Average FSR: " << avgFsr << std::endl;
    }

    return 0;
}