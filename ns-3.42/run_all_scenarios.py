import subprocess
import csv
import os

algos = ["ADR-MIN", "ADR-MAX", "ADR-AVG", "Q-Learning", "DQN", "DDQN-PER"]
scenarios = []

# Scenario 1 : 10 à 100, 1 jour
scenarios += [(n, 86400, False) for n in range(10, 101, 10)]
# Scenario 2 : 100 à 1000, 1 jour
scenarios += [(n, 86400, False) for n in range(100, 1001, 100)]
# Scenario 3 : 100, 1 à 7 jours
scenarios += [(100, 86400*d, False) for d in range(1, 8)]
# Scenario 4 : 1000, 1 à 7 jours
scenarios += [(1000, 86400*d, False) for d in range(1, 8)]

# Duplique pour obstacles
scenarios += [(n, t, True) for (n, t, _) in scenarios]

results_file = "all_results.csv"
with open(results_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["nDevices", "simTime", "obstacles", "algorithm", "PDR", "EC"])
    for algo in algos:
        for nDevices, simTime, obstacles in scenarios:
            print(f"Run: Algo={algo}, nDevices={nDevices}, simTime={simTime}, obstacles={obstacles}")
            cmd = [
                "./ns3", "run",
                f"\"scratch/lorawan-comparison-working --nDevices={nDevices} --simTime={simTime} --obstacles={'true' if obstacles else 'false'} --algorithm={algo}\""
            ]
            subprocess.run(" ".join(cmd), shell=True)
            # Lis le résultat temporaire (temp_results.txt généré par ton C++)
            with open("temp_results.txt") as f:
                line = f.readline().strip()
                PDR, EC = line.split(",")
            writer.writerow([nDevices, simTime, "obstacles" if obstacles else "open", algo, PDR, EC])
print(f"Tous les résultats sont dans {results_file}")
