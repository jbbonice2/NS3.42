#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lorawan-module.h"
#include "ns3/propagation-module.h"
#include "ns3/log.h"
#include <random>
#include <vector>
#include <map>
#include <fstream>
#include <cmath>

NS_LOG_COMPONENT_DEFINE("LoRaEnergyEfficientSimulation");

using namespace ns3;

class LoRaEndDevice : public Object {
public:
    static TypeId GetTypeId(void) {
        static TypeId tid = TypeId("LoRaEndDevice")
            .SetParent<Object>()
            .SetGroupName("LoRa")
            .AddConstructor<LoRaEndDevice>();
        return tid;
    }

    LoRaEndDevice() : id(0), node(nullptr), netDevice(nullptr), bandwidth(0), sf(0), transmissions(0), successfulTransmissions(0) {
        NS_LOG_DEBUG("Creating LoRaEndDevice with default constructor");
        InitializeUCB();
        InitializeEnergyModel();
    }

    LoRaEndDevice(uint32_t id, Ptr<Node> node, Ptr<lorawan::LoraNetDevice> netDevice, double bandwidth, uint32_t sf)
        : id(id), node(node), netDevice(netDevice), bandwidth(bandwidth), sf(sf), transmissions(0), successfulTransmissions(0) {
        NS_LOG_DEBUG("Creating LoRaEndDevice with id " << id);
        NS_ASSERT(node != nullptr);
        NS_ASSERT(netDevice != nullptr);
        InitializeUCB();
        InitializeEnergyModel();
    }

    void InitializeUCB() {
        channels = {920.6, 921.0, 921.4, 921.8, 922.2};
        tps = {-3, 1, 5, 9, 13};
        for (double channel : channels) {
            for (double tp : tps) {
                rewards[{channel, tp}] = 0.0;
                selections[{channel, tp}] = 0;
                variances[{channel, tp}] = 0.0;
                tpCounts[tp] = 0;
            }
        }
    }

    void InitializeEnergyModel() {
        eWU = 56.1 * tWU; // mWh
        eProc = 85.8 * tProc; // mWh
        eR = 66.0 * tR; // mWh
        pMCU = 29.7; // mW
        nP = 8; // preamble symbols
        nPayload = 40; // average 36-44 bytes
    }

    std::pair<double, double> SelectParameters(uint32_t t) {
        if (transmissions < channels.size() * tps.size()) {
            size_t idx = transmissions;
            double channel = channels[idx / tps.size()];
            double tp = tps[idx % tps.size()];
            return {channel, tp};
        } else {
            double maxUCB = -std::numeric_limits<double>::max();
            std::pair<double, double> bestParam;
            for (double channel : channels) {
                for (double tp : tps) {
                    auto key = std::make_pair(channel, tp);
                    double avgReward = selections[key] > 0 ? rewards[key] / selections[key] : 0.0;
                    double variance = variances[key] + std::sqrt(2.0 * std::log(t) / (selections[key] + 1e-10));
                    double ucb = avgReward + std::sqrt((std::log(t) / (selections[key] + 1e-10)) * std::min(0.25, variance));
                    if (ucb > maxUCB) {
                        maxUCB = ucb;
                        bestParam = key;
                    }
                }
            }
            return bestParam;
        }
    }

    void UpdateUCB(std::pair<double, double> param, bool ack, double eToA) {
        transmissions++;
        selections[param]++;
        if (ack) {
            successfulTransmissions++;
            rewards[param] += 1.0 / eToA;
            tpCounts[param.second]++;
        }
        variances[param] = 0.25; // Simplified as per UCB1-tuned
        NS_LOG_DEBUG("Device " << id << " updated UCB: channel=" << param.first << ", tp=" << param.second << ", ack=" << ack);
    }

    double CalculateEnergyConsumption(double tp, double tToA) {
        double pTx = std::pow(10, (tp / 10.0)) * 1000.0; // Convert dBm to mW
        double eTx = (pMCU + pTx) * tToA; // mWh
        return eWU + eProc + eTx + eR; // Total active energy
    }

    double CalculateTToA() {
        double tSymbol = std::pow(2, sf) / bandwidth; // seconds
        double tPreamble = (4.25 + nP) * tSymbol;
        double tPayload = nPayload * tSymbol;
        return (tPreamble + tPayload) / 3600.0; // Convert to hours for mWh
    }

    uint32_t GetTransmissions() const { return transmissions; }
    uint32_t GetSuccessfulTransmissions() const { return successfulTransmissions; }
    void IncrementSuccessfulTransmissions() { successfulTransmissions++; }
    std::map<double, uint32_t> GetTPCounts() const { return tpCounts; }
    Ptr<lorawan::LoraNetDevice> GetNetDevice() const { return netDevice; }

private:
    uint32_t id;
    Ptr<Node> node;
    Ptr<lorawan::LoraNetDevice> netDevice;
    double bandwidth;
    uint32_t sf;
    std::vector<double> channels;
    std::vector<double> tps;
    std::map<std::pair<double, double>, double> rewards;
    std::map<std::pair<double, double>, uint32_t> selections;
    std::map<std::pair<double, double>, double> variances;
    std::map<double, uint32_t> tpCounts;
    uint32_t transmissions;
    uint32_t successfulTransmissions;
    double eWU, eProc, eR, pMCU;
    uint32_t nP, nPayload;
    double tWU = 0.01, tProc = 0.005, tR = 0.01; // Example times in hours
};

class LoRaGateway : public Object {
public:
    static TypeId GetTypeId(void) {
        static TypeId tid = TypeId("LoRaGateway")
            .SetParent<Object>()
            .SetGroupName("LoRa")
            .AddConstructor<LoRaGateway>();
        return tid;
    }

    LoRaGateway() : node(nullptr), netDevice(nullptr), receivedPackets(0) {
        receivableChannels = {921.0, 921.4, 921.8};
        NS_LOG_DEBUG("Creating LoRaGateway with default constructor");
    }

    LoRaGateway(Ptr<Node> node, Ptr<lorawan::LoraNetDevice> netDevice)
        : node(node), netDevice(netDevice), receivedPackets(0) {
        receivableChannels = {921.0, 921.4, 921.8};
        NS_LOG_DEBUG("Creating LoRaGateway with node and netDevice");
        NS_ASSERT(node != nullptr);
        NS_ASSERT(netDevice != nullptr);
    }

    void Receive(Ptr<const Packet> packet) {
        Ptr<Packet> copy = packet->Copy();
        lorawan::LoraTag tag;
        if (copy->RemovePacketTag(tag)) {
            double frequency = tag.GetFrequency();
            double rxPower = tag.GetReceivePower();
            bool channelMatch = std::find(receivableChannels.begin(), receivableChannels.end(), frequency) != receivableChannels.end();
            if (channelMatch && rxPower > -120.0) { // Example threshold in dBm
                receivedPackets++;
                NS_LOG_DEBUG("Gateway received packet: freq=" << frequency << ", rxPower=" << rxPower);
            } else {
                NS_LOG_DEBUG("Gateway failed to receive packet: freq=" << frequency << ", rxPower=" << rxPower);
            }
        } else {
            NS_LOG_DEBUG("Gateway received packet with no LoraTag");
        }
    }

    uint32_t GetReceivedPackets() const { return receivedPackets; }
    Ptr<lorawan::LoraNetDevice> GetNetDevice() const { return netDevice; }
    Ptr<Node> GetNode() const { return node; }

private:
    Ptr<Node> node;
    Ptr<lorawan::LoraNetDevice> netDevice;
    std::vector<double> receivableChannels;
    uint32_t receivedPackets;
};

class EGreedyEndDevice : public LoRaEndDevice {
public:
    static TypeId GetTypeId(void) {
        static TypeId tid = TypeId("EGreedyEndDevice")
            .SetParent<LoRaEndDevice>()
            .SetGroupName("LoRa")
            .AddConstructor<EGreedyEndDevice>();
        return tid;
    }

    EGreedyEndDevice() : LoRaEndDevice(), epsilon(0.1) {
        NS_LOG_DEBUG("Creating EGreedyEndDevice with default constructor");
        channels = {920.6, 921.0, 921.4, 921.8, 922.2};
        tps = {-3, 1, 5, 9, 13};
    }

    EGreedyEndDevice(uint32_t id, Ptr<Node> node, Ptr<lorawan::LoraNetDevice> netDevice, double bandwidth, uint32_t sf, double epsilon)
        : LoRaEndDevice(id, node, netDevice, bandwidth, sf), epsilon(epsilon) {
        NS_LOG_DEBUG("Creating EGreedyEndDevice with id " << id);
        channels = {920.6, 921.0, 921.4, 921.8, 922.2};
        tps = {-3, 1, 5, 9, 13};
    }

    std::pair<double, double> SelectParameters(uint32_t t) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(0.0, 1.0);
        if (dis(gen) < epsilon) {
            std::uniform_int_distribution<> chDis(0, channels.size() - 1);
            std::uniform_int_distribution<> tpDis(0, tps.size() - 1);
            return {channels[chDis(gen)], tps[tpDis(gen)]};
        } else {
            double maxReward = -std::numeric_limits<double>::max();
            std::pair<double, double> bestParam;
            for (double channel : channels) {
                for (double tp : tps) {
                    auto key = std::make_pair(channel, tp);
                    double avgReward = selections[key] > 0 ? rewards[key] / selections[key] : 0.0;
                    if (avgReward > maxReward) {
                        maxReward = avgReward;
                        bestParam = key;
                    }
                }
            }
            return bestParam;
        }
    }

private:
    double epsilon;
    std::vector<double> channels;
    std::vector<double> tps;
    std::map<std::pair<double, double>, double> rewards;
    std::map<std::pair<double, double>, uint32_t> selections;
};

class ADRLiteEndDevice : public LoRaEndDevice {
public:
    static TypeId GetTypeId(void) {
        static TypeId tid = TypeId("ADRLiteEndDevice")
            .SetParent<LoRaEndDevice>()
            .SetGroupName("LoRa")
            .AddConstructor<ADRLiteEndDevice>();
        return tid;
    }

    ADRLiteEndDevice() : LoRaEndDevice(), currentIdx(0) {
        NS_LOG_DEBUG("Creating ADRLiteEndDevice with default constructor");
        InitializeParamList();
    }

    ADRLiteEndDevice(uint32_t id, Ptr<Node> node, Ptr<lorawan::LoraNetDevice> netDevice, double bandwidth, uint32_t sf)
        : LoRaEndDevice(id, node, netDevice, bandwidth, sf), currentIdx(0) {
        NS_LOG_DEBUG("Creating ADRLiteEndDevice with id " << id);
        InitializeParamList();
    }

    void InitializeParamList() {
        std::vector<double> channels = {920.6, 922.2, 921.0, 921.4, 921.8};
        std::vector<double> tps = {-3, 1, 5, 9, 13};
        for (double channel : channels) {
            for (double tp : tps) {
                paramList.push_back({channel, tp});
            }
        }
        if (!paramList.empty()) {
            currentIdx = paramList.size() - 1;
        }
    }

    std::pair<double, double> SelectParameters(uint32_t t) {
        return paramList[currentIdx];
    }

    void UpdateUCB(std::pair<double, double> param, bool ack, double eToA) {
        LoRaEndDevice::UpdateUCB(param, ack, eToA);
        int lastIdx = currentIdx;
        if (ack) {
            currentIdx = (0 + lastIdx) / 2;
        } else {
            currentIdx = (paramList.size() - 1 + lastIdx) / 2;
        }
        if (currentIdx >= paramList.size()) currentIdx = paramList.size() - 1;
    }

private:
    std::vector<std::pair<double, double>> paramList;
    size_t currentIdx;
};

class FixedAllocationEndDevice : public LoRaEndDevice {
public:
    static TypeId GetTypeId(void) {
        static TypeId tid = TypeId("FixedAllocationEndDevice")
            .SetParent<LoRaEndDevice>()
            .SetGroupName("LoRa")
            .AddConstructor<FixedAllocationEndDevice>();
        return tid;
    }

    FixedAllocationEndDevice() : LoRaEndDevice(), fixedChannel(920.6), fixedTP(-3) {
        NS_LOG_DEBUG("Creating FixedAllocationEndDevice with default constructor");
    }

    FixedAllocationEndDevice(uint32_t id, Ptr<Node> node, Ptr<lorawan::LoraNetDevice> netDevice, double bandwidth, uint32_t sf, double channel)
        : LoRaEndDevice(id, node, netDevice, bandwidth, sf), fixedChannel(channel), fixedTP(-3) {
        NS_LOG_DEBUG("Creating FixedAllocationEndDevice with id " << id);
    }

    std::pair<double, double> SelectParameters(uint32_t t) {
        return {fixedChannel, fixedTP};
    }

private:
    double fixedChannel;
    double fixedTP;
};

struct TransmissionData {
    Ptr<LoRaEndDevice> device;
    uint32_t transmissionIdx;
    std::pair<double, double> param;
    double tToA;
    Ptr<Packet> packet;
    Ptr<LogDistancePropagationLossModel> loss;
    Ptr<LoRaGateway> gateway;
    double* totalEnergy;
    uint32_t* totalTransmissions;
    uint32_t* totalSuccessfulTransmissions;
    std::map<double, uint32_t>* totalTPCounts;
};

void HandleTransmission(TransmissionData* data) {
    NS_LOG_DEBUG("Handling transmission for device " << data->device->GetTransmissions());
    Ptr<lorawan::LoraNetDevice> netDevice = data->device->GetNetDevice();
    NS_ASSERT(netDevice != nullptr);
    Ptr<lorawan::ClassAEndDeviceLorawanMac> mac = DynamicCast<lorawan::ClassAEndDeviceLorawanMac>(netDevice->GetMac());
    NS_ASSERT(mac != nullptr);
    Ptr<lorawan::EndDeviceLoraPhy> phy = DynamicCast<lorawan::EndDeviceLoraPhy>(netDevice->GetPhy());
    NS_ASSERT(phy != nullptr);

    // Configure device parameters
    mac->SetDataRate(0); // SF7, BW=125 kHz
    phy->SetAttribute("TxPower", DoubleValue(data->param.second));
    phy->SetAttribute("Frequency", DoubleValue(data->param.first));

    // Add LoraTag to packet
    lorawan::LoraTag tag;
    tag.SetFrequency(data->param.first);
    tag.SetDataRate(0);
    Ptr<MobilityModel> senderMobility = netDevice->GetNode()->GetObject<MobilityModel>();
    Ptr<MobilityModel> receiverMobility = data->gateway->GetNode()->GetObject<MobilityModel>();
    double rxPower = data->param.second - data->loss->CalcRxPower(data->param.second, senderMobility, receiverMobility);
    tag.SetReceivePower(rxPower);
    data->packet->AddPacketTag(tag);

    // Simulate transmission
    mac->Send(data->packet);

    // Update metrics
    *(data->totalEnergy) += data->device->CalculateEnergyConsumption(data->param.second, data->tToA);
    *(data->totalTransmissions) += 1;
    auto tpCounts = data->device->GetTPCounts();
    for (const auto& [tp, count] : tpCounts) {
        (*data->totalTPCounts)[tp] += count;
    }

    // Update UCB (assume reception status will be updated via trace)
    data->device->UpdateUCB(data->param, false, data->tToA); // Default to false, updated in Receive

    // Clean up
    delete data;
}

void SimulateScenario(uint32_t nDevices, std::string method, std::ofstream& tpFile, std::ofstream& successFile, std::ofstream& energyFile) {
    NS_LOG_DEBUG("Starting SimulateScenario with " << nDevices << " devices, method: " << method);

    // Create nodes
    NodeContainer endDeviceNodes, gatewayNodes;
    endDeviceNodes.Create(nDevices);
    gatewayNodes.Create(1);

    // Set up mobility
    MobilityHelper mobility;
    mobility.SetPositionAllocator("ns3::GridPositionAllocator",
                                 "MinX", DoubleValue(0.0),
                                 "MinY", DoubleValue(0.0),
                                 "DeltaX", DoubleValue(100.0),
                                 "DeltaY", DoubleValue(100.0),
                                 "GridWidth", UintegerValue(5),
                                 "LayoutType", StringValue("RowFirst"));
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(endDeviceNodes);
    mobility.Install(gatewayNodes);

    // Set up propagation loss and delay models
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    Ptr<ConstantSpeedPropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();

    // Set up LoRaWAN channel
    Ptr<lorawan::LoraChannel> channel = CreateObject<lorawan::LoraChannel>(loss, delay);
    NS_LOG_DEBUG("Created LoraChannel");

    // Set up LoRaWAN PHY
    lorawan::LoraPhyHelper phyHelper;
    phyHelper.SetChannel(channel);

    // Set up LoRaWAN MAC
    lorawan::LorawanMacHelper macHelper;
    lorawan::LoraHelper loraHelper;

    // Configure end devices
    macHelper.Set("Class", StringValue("ns3::lorawan::ClassAEndDeviceLorawanMac"));
    NetDeviceContainer endDeviceNetDevices = loraHelper.Install(phyHelper, macHelper, endDeviceNodes);
    NS_LOG_DEBUG("Installed end device net devices: " << endDeviceNetDevices.GetN());

    // Configure gateway
    macHelper.Set("Class", StringValue("ns3::lorawan::GatewayLorawanMac"));
    NetDeviceContainer gatewayNetDevices = loraHelper.Install(phyHelper, macHelper, gatewayNodes);
    Ptr<lorawan::LoraNetDevice> gwDevice = DynamicCast<lorawan::LoraNetDevice>(gatewayNetDevices.Get(0));
    NS_ASSERT(gwDevice != nullptr);
    NS_LOG_DEBUG("Created gateway net device");
    Ptr<LoRaGateway> gw = CreateObject<LoRaGateway>(gatewayNodes.Get(0), gwDevice);

    // Configure gateway MAC frequencies
    Ptr<lorawan::GatewayLorawanMac> gwMac = DynamicCast<lorawan::GatewayLorawanMac>(gwDevice->GetMac());
    NS_ASSERT(gwMac != nullptr);
    gwMac->SetAttribute("Frequencies", StringValue("921.0,921.4,921.8"));

    // Connect reception trace
    gwDevice->GetMac()->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&LoRaGateway::Receive, gw));

    // Configure end devices and create LoRaEndDevice instances
    std::vector<Ptr<LoRaEndDevice>> endDevices;
    std::vector<double> channels = {920.6, 921.0, 921.4, 921.8, 922.2};
    for (uint32_t i = 0; i < nDevices; ++i) {
        Ptr<lorawan::LoraNetDevice> netDevice = DynamicCast<lorawan::LoraNetDevice>(endDeviceNetDevices.Get(i));
        NS_ASSERT(netDevice != nullptr);
        Ptr<lorawan::ClassAEndDeviceLorawanMac> mac = DynamicCast<lorawan::ClassAEndDeviceLorawanMac>(netDevice->GetMac());
        NS_ASSERT(mac != nullptr);
        mac->SetDataRate(0); // Maps to SF7, BW=125 kHz
        if (method == "fixed") {
            double channel = channels[i % channels.size()];
            endDevices.push_back(CreateObject<FixedAllocationEndDevice>(i, endDeviceNodes.Get(i), netDevice, 125e3, 7, channel));
        } else if (method == "adr-lite") {
            endDevices.push_back(CreateObject<ADRLiteEndDevice>(i, endDeviceNodes.Get(i), netDevice, 125e3, 7));
        } else if (method == "epsilon-greedy") {
            endDevices.push_back(CreateObject<EGreedyEndDevice>(i, endDeviceNodes.Get(i), netDevice, 125e3, 7, 0.1));
        } else {
            endDevices.push_back(CreateObject<LoRaEndDevice>(i, endDeviceNodes.Get(i), netDevice, 125e3, 7));
        }
        NS_LOG_DEBUG("Created end device " << i << " with method " << method);
    }

    double totalEnergy = 0.0;
    uint32_t totalTransmissions = 0;
    uint32_t totalSuccessfulTransmissions = 0;
    std::map<double, uint32_t> totalTPCounts;

    // Schedule 200 transmissions per device
    for (uint32_t t = 1; t <= 200 * nDevices; ++t) {
        uint32_t deviceIdx = (t - 1) % nDevices;
        auto device = endDevices[deviceIdx];
        auto param = device->SelectParameters(t);
        double tToA = device->CalculateTToA();

        TransmissionData* data = new TransmissionData{device, t, param, tToA, Create<Packet>(40), loss, gw, &totalEnergy, &totalTransmissions, &totalSuccessfulTransmissions, &totalTPCounts};
        Simulator::Schedule(Seconds(t * 1.0), &HandleTransmission, data); // 1-second spacing
    }

    // Run the simulation
    Simulator::Run();

    // Collect results
    totalSuccessfulTransmissions = gw->GetReceivedPackets();

    double successRate = totalTransmissions > 0 ? static_cast<double>(totalSuccessfulTransmissions) / totalTransmissions : 0.0;
    double energyEfficiency = totalEnergy > 0 ? successRate / totalEnergy : 0.0;
    uint32_t totalTPSelections = 0;
    for (const auto& [tp, count] : totalTPCounts) {
        totalTPSelections += count;
    }

    tpFile << method << "," << nDevices;
    for (double tp : {-3, 1, 5, 9, 13}) {
        double ratio = totalTPSelections > 0 ? static_cast<double>(totalTPCounts[tp]) / totalTPSelections : 0.0;
        tpFile << "," << ratio;
    }
    tpFile << "\n";

    successFile << method << "," << nDevices << "," << successRate << "\n";
    energyFile << method << "," << nDevices << "," << energyEfficiency << "\n";

    NS_LOG_DEBUG("Completed simulation: method=" << method << ", devices=" << nDevices << ", successRate=" << successRate << ", energyEfficiency=" << energyEfficiency);
}

void WritePlotScript() {
    std::ofstream plotScript("plot_results.py");
    plotScript << R"(
import pandas as pd
import matplotlib.pyplot as plt

# TP Ratio Plot
tp_data = pd.read_csv('tp_ratio.csv')
devices = [10, 15, 20, 25, 30]
methods = ['proposed', 'epsilon-greedy', 'adr-lite']
tps = ['-3dBm', '1dBm', '5dBm', '9dBm', '13dBm']
fig, ax = plt.subplots()
for method in methods:
    ratios = tp_data[tp_data['Method'] == method][tps].mean()
    ax.plot(tps, ratios, label=method, marker='o')
ax.set_xlabel('Transmission Power (dBm)')
ax.set_ylabel('Selection Ratio')
ax.legend()
plt.savefig('tp_ratio.png')

# Transmission Success Rate Plot
success_data = pd.read_csv('success_rate.csv')
fig, ax = plt.subplots()
for method in methods + ['fixed']:
    data = success_data[success_data['Method'] == method]
    ax.plot(data['Devices'], data['SuccessRate'], label=method, marker='o')
ax.set_xlabel('Number of Devices')
ax.set_ylabel('Transmission Success Rate')
ax.legend()
plt.savefig('success_rate.png')

# Energy Efficiency Plot
energy_data = pd.read_csv('energy_efficiency.csv')
fig, ax = plt.subplots()
for method in methods + ['fixed']:
    data = energy_data[energy_data['Method'] == method]
    ax.plot(data['Devices'], data['EnergyEfficiency'], label=method, marker='o')
ax.set_xlabel('Number of Devices')
ax.set_ylabel('Energy Efficiency')
ax.legend()
plt.savefig('energy_efficiency.png')
plt.show()
)";
    plotScript.close();
}

int main(int argc, char* argv[]) {
    LogComponentEnable("LoRaEnergyEfficientSimulation", LOG_LEVEL_DEBUG);
    LogComponentEnable("LoraChannel", LOG_LEVEL_DEBUG);
    LogComponentEnable("LoraPhyHelper", LOG_LEVEL_DEBUG);
    LogComponentEnable("LorawanMacHelper", LOG_LEVEL_DEBUG);
    LogComponentEnable("ClassAEndDeviceLorawanMac", LOG_LEVEL_DEBUG);
    LogComponentEnable("GatewayLorawanMac", LOG_LEVEL_DEBUG);

    std::ofstream tpFile("tp_ratio.csv");
    std::ofstream successFile("success_rate.csv");
    std::ofstream energyFile("energy_efficiency.csv");

    tpFile << "Method,Devices,-3dBm,1dBm,5dBm,9dBm,13dBm\n";
    successFile << "Method,Devices,SuccessRate\n";
    energyFile << "Method,Devices,EnergyEfficiency\n";

    WritePlotScript();

    std::vector<uint32_t> nDevicesList = {10, 15, 20, 25, 30};
    std::vector<std::string> methods = {"proposed", "epsilon-greedy", "adr-lite", "fixed"};

    for (uint32_t nDevices : nDevicesList) {
        for (const auto& method : methods) {
            NS_LOG_INFO("Running simulation for " << method << " with " << nDevices << " devices");
            SimulateScenario(nDevices, method, tpFile, successFile, energyFile);
            Simulator::Destroy();
        }
    }

    tpFile.close();
    successFile.close();
    energyFile.close();

    return 0;
}