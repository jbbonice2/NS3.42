
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
