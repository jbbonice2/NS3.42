import pandas as pd
import matplotlib.pyplot as plt

# Charger les résultats globaux
results_file = "all_results.csv"
df = pd.read_csv(results_file)

# PDR vs nDevices (1 jour, open space)
plt.figure(figsize=(10,6))
for algo in df['algorithm'].unique():
    data = df[(df['algorithm'] == algo) & (df['simTime'] == 86400) & (df['obstacles'] == 'open')]
    plt.plot(data['nDevices'], data['PDR'], marker='o', label=algo)
plt.xlabel("Number of Nodes")
plt.ylabel("PDR")
plt.title("PDR vs Number of Nodes (1 jour, open space)")
plt.legend()
plt.grid(True)
plt.savefig("pdr_vs_nodes_open.png")
plt.close()

# EC vs nDevices (1 jour, open space)
plt.figure(figsize=(10,6))
for algo in df['algorithm'].unique():
    data = df[(df['algorithm'] == algo) & (df['simTime'] == 86400) & (df['obstacles'] == 'open')]
    plt.plot(data['nDevices'], data['EC'], marker='o', label=algo)
plt.xlabel("Number of Nodes")
plt.ylabel("Energy Consumption (mJ)")
plt.title("EC vs Number of Nodes (1 jour, open space)")
plt.legend()
plt.grid(True)
plt.savefig("ec_vs_nodes_open.png")
plt.close()

# Tu peux dupliquer les blocs pour obstacles, ou d'autres scénarios (simTime, etc.)
