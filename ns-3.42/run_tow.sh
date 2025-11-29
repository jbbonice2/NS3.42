#!/bin/bash

# =============================================================================
# Scripts de simulation pour l'implémentation ToW LoRaWAN
# =============================================================================

# Configuration des chemins
NS3_PATH="/media/sergeo/Travaux/ns-allinone-3.42/ns-3.42"
SIMULATION_DIR="$(pwd)/simulation_results"

# Créer le répertoire de résultats
mkdir -p "$SIMULATION_DIR"

echo "=== Simulation ToW LoRaWAN Channel Selection ==="
echo "Répertoire des résultats: $SIMULATION_DIR"

# =============================================================================
# Script 1: Scénario 1 - FSR vs Nombre de dispositifs
# =============================================================================

echo "Démarrage du Scénario 1: FSR vs Nombre de dispositifs"

# Algorithmes à tester
algorithms=("ToW" "UCB1-Tuned" "EpsilonGreedy" "Random")

run_scenario1() {
    echo "Exécution du Scénario 1..."

    cd "$NS3_PATH"

    for algo in "${algorithms[@]}"; do
        echo "  Algorithme: $algo"

        # Compiler et exécuter la simulation
        # ./ns3 run "lorawan-tow --scenario=1 --algorithm=$algo" > "$SIMULATION_DIR/scenario1_${algo}_log.txt" 2>&1
        ./ns3 run "lorawan-tow --scenario=1 --algorithm=$algo" > "$SIMULATION_DIR/scenario1_${algo}_log.log" 2>&1

        # Vérifier si la simulation s'est bien déroulée
        if [ $? -eq 0 ]; then
            echo "    ✓ Simulation terminée avec succès"

            # Déplacer les fichiers de résultats
            if [ -f "scenario1_${algo}.txt" ]; then
                mv "scenario1_${algo}.txt" "$SIMULATION_DIR/"
                echo "    ✓ Résultats sauvegardés: scenario1_${algo}.txt"
            else
                echo "    ⚠ Fichier de résultats non trouvé"
            fi
        else
            echo "    ✗ Erreur lors de la simulation"
            echo "    Voir le log: $SIMULATION_DIR/scenario1_${algo}_log.log"
        fi
    done

    echo "Scénario 1 terminé"
}

# =============================================================================
# Script 2: Scénario 2 - Canaux dynamiques
# =============================================================================

run_scenario2() {
    echo "Exécution du Scénario 2: Canaux dynamiques..."

    cd "$NS3_PATH"

    # Exécuter 10 fois chaque algorithme pour obtenir la moyenne
    for algo in "${algorithms[@]}"; do
        echo "  Algorithme: $algo (10 exécutions)"

        total_fsr=0
        successful_runs=0

        for run in {1..10}; do
            echo "    Exécution $run/10..."

            # Exécuter la simulation
            timeout 600s ./ns3 run "lorawan-tow --scenario=2 --algorithm=$algo" > "$SIMULATION_DIR/scenario2_${algo}_run${run}_log.log" 2>&1

            if [ $? -eq 0 ]; then
                # Déplacer les résultats avec un suffixe
                if [ -f "scenario2_${algo}.txt" ]; then
                    cp "scenario2_${algo}.txt" "$SIMULATION_DIR/scenario2_${algo}_run${run}.txt"

                    # Extraire le FSR pour calculer la moyenne
                    fsr=$(grep "Average FSR:" "scenario2_${algo}.txt" | cut -d':' -f2 | tr -d ' ')
                    if [[ $fsr =~ ^[0-9]+\.?[0-9]*$ ]]; then
                        total_fsr=$(echo "$total_fsr + $fsr" | bc -l)
                        successful_runs=$((successful_runs + 1))
                    fi

                    rm "scenario2_${algo}.txt"  # Nettoyer le fichier temporaire
                fi
                echo "      ✓ Exécution $run terminée"
            else
                echo "      ✗ Exécution $run échouée (timeout ou erreur)"
            fi
        done

        # Calculer et sauvegarder la moyenne
        if [ $successful_runs -gt 0 ]; then
            avg_fsr=$(echo "scale=6; $total_fsr / $successful_runs" | bc -l)
            echo "$algo Average FSR (10 runs): $avg_fsr" > "$SIMULATION_DIR/scenario2_${algo}_average.txt"
            echo "  ✓ FSR moyen: $avg_fsr ($successful_runs/$10 exécutions réussies)"
        else
            echo "  ✗ Aucune exécution réussie"
        fi
    done

    echo "Scénario 2 terminé"
}

# =============================================================================
# Script 3: Génération des graphiques avec Python
# =============================================================================

generate_plots() {
    echo "Génération des graphiques..."

    cd "$SIMULATION_DIR"

    # Créer le script Python pour les graphiques
    cat > plot_results.py << 'EOF'
#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os
import re
from collections import defaultdict

def load_scenario1_data(algorithm):
    """Charger les données du scénario 1"""
    filename = f"scenario1_{algorithm}.txt"
    if not os.path.exists(filename):
        print(f"Fichier {filename} introuvable")
        return [], []

    devices = []
    fsr = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    devices.append(int(parts[0]))
                    fsr.append(float(parts[1]))
                except ValueError:
                    continue

    return devices, fsr

def load_scenario2_data(algorithm):
    """Charger les données du scénario 2 - moyennes sur 10 exécutions"""
    filename = f"scenario2_{algorithm}_average.txt"
    if not os.path.exists(filename):
        print(f"Fichier {filename} introuvable")
        return 0.0

    with open(filename, 'r') as f:
        line = f.readline()
        match = re.search(r'Average FSR.*:\s*([0-9.]+)', line)
        if match:
            return float(match.group(1))

    return 0.0

def load_scenario2_channel_data(algorithm):
    """Charger les données de transmissions par canal (première exécution)"""
    filename = f"scenario2_{algorithm}_run1.txt"
    if not os.path.exists(filename):
        print(f"Fichier {filename} introuvable")
        return {}

    channel_data = {}
    with open(filename, 'r') as f:
        for line in f:
            if 'Channel' in line and 'successful transmissions' in line:
                match = re.search(r'Channel (\d+): (\d+) successful', line)
                if match:
                    channel = int(match.group(1))
                    count = int(match.group(2))
                    channel_data[channel] = count

    return channel_data

def plot_scenario1():
    """Générer le graphique du scénario 1 (Fig. 3)"""
    algorithms = ["ToW", "UCB1-Tuned", "EpsilonGreedy", "Random"]
    colors = ['b-o', 'r-s', 'g-^', 'm-d']
    labels = ['ToW', 'UCB1-T', 'ε-greedy', 'Random']

    plt.figure(figsize=(10, 6))

    for i, (algo, color, label) in enumerate(zip(algorithms, colors, labels)):
        devices, fsr = load_scenario1_data(algo)
        if devices and fsr:
            plt.plot(devices, fsr, color, label=label, linewidth=2, markersize=6)

    plt.xlabel('The number of LoRa devices')
    plt.ylabel('FSR')
    plt.title('Frame Success Rate vs Number of LoRa Devices')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 32)
    plt.ylim(0.4, 1.0)

    plt.tight_layout()
    plt.savefig('figure3_fsr_vs_devices.png', dpi=300, bbox_inches='tight')
    plt.savefig('figure3_fsr_vs_devices.pdf', bbox_inches='tight')
    print("✓ Figure 3 générée: figure3_fsr_vs_devices.png/.pdf")
    plt.close()

def plot_scenario2_channels():
    """Générer les graphiques du scénario 2 (Fig. 4)"""
    algorithms = ["ToW", "UCB1-Tuned", "EpsilonGreedy", "Random"]
    titles = ['(a) ToW', '(b) UCB1-Tuned', '(c) ε-greedy', '(d) Random']

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    # Périodes pour les lignes verticales
    time_periods = [10, 20, 30, 40]

    for i, (algo, title) in enumerate(zip(algorithms, titles)):
        channel_data_per_minute = defaultdict(lambda: defaultdict(list))
        filename = f"scenario2_{algo}_traces.csv"  # Utilise le nouveau CSV
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    parts = line.strip().split(',')
                    minute = int(parts[0])
                    for i, ch in enumerate([0,2,4,6,8]):
                        channel_data_per_minute[ch].append(cumulative_success := channel_data_per_minute[ch][-1] + int(parts[i+1]) if channel_data_per_minute[ch] else int(parts[i+1]))
        
        time = list(range(40))
        for j, (channel, label, color) in enumerate(zip([0,2,4], ['CH1', 'CH3', 'CH5'], ['blue', 'red', 'green'])):
            ax.plot(time, channel_data_per_minute[channel], color=color, label=label, linewidth=2)

        # Lignes verticales pour marquer les changements de période
        for t in [10, 20, 30]:
            ax.axvline(x=t, color='gray', linestyle='--', alpha=0.5)

        ax.set_xlabel('Time (min.)')
        ax.set_ylabel('The number of successful transmissions')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 40)

        # Adapter les limites Y selon l'algorithme
        if algo == "Random":
            ax.set_ylim(0, 40)
        else:
            ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('figure4_channel_transmissions.png', dpi=300, bbox_inches='tight')
    plt.savefig('figure4_channel_transmissions.pdf', bbox_inches='tight')
    print("✓ Figure 4 générée: figure4_channel_transmissions.png/.pdf")
    plt.close()

def plot_scenario2_average():
    """Générer le graphique des FSR moyens (Fig. 5)"""
    algorithms = ["ToW", "UCB1-Tuned", "EpsilonGreedy", "Random"]
    labels = ['ToW', 'UCB1-T', 'ε-greedy', 'Random']

    fsr_values = []
    for algo in algorithms:
        fsr = load_scenario2_data(algo)
        fsr_values.append(fsr)

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, fsr_values, color=['blue', 'red', 'green', 'magenta'], alpha=0.7)

    # Ajouter les valeurs sur les barres
    for bar, value in zip(bars, fsr_values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}', ha='center', va='bottom')

    plt.ylabel('Average FSR')
    plt.title('Average Frame Success Rate in Scenario 2')
    plt.ylim(0, 1.0)
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('figure5_average_fsr.png', dpi=300, bbox_inches='tight')
    plt.savefig('figure5_average_fsr.pdf', bbox_inches='tight')
    print("✓ Figure 5 générée: figure5_average_fsr.png/.pdf")
    plt.close()

def main():
    print("Génération des graphiques...")

    # Vérifier la disponibilité de matplotlib
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Erreur: matplotlib et numpy sont requis")
        print("Installation: pip install matplotlib numpy")
        return

    # Générer tous les graphiques
    plot_scenario1()
    plot_scenario2_channels()
    plot_scenario2_average()

    print("Tous les graphiques ont été générés avec succès!")

if __name__ == "__main__":
    main()
EOF

    # Exécuter le script Python
    python3 plot_results.py

    if [ $? -eq 0 ]; then
        echo "✓ Graphiques générés avec succès"
    else
        echo "⚠ Erreur lors de la génération des graphiques"
        echo "Assurez-vous que matplotlib et numpy sont installés:"
        echo "pip install matplotlib numpy"
    fi
}

# =============================================================================
# Script principal
# =============================================================================

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --scenario1    Exécuter uniquement le scénario 1"
    echo "  --scenario2    Exécuter uniquement le scénario 2"
    echo "  --plots        Générer uniquement les graphiques"
    echo "  --all          Exécuter tous les scénarios et générer les graphiques (défaut)"
    echo "  --help         Afficher cette aide"
    echo ""
    echo "Configuration requise:"
    echo "  - NS-3.42 installé avec le module LoRaWAN"
    echo "  - Python 3 avec matplotlib et numpy pour les graphiques"
    echo ""
    echo "Avant d'exécuter:"
    echo "  1. Modifier NS3_PATH dans ce script"
    echo "  2. Copier lorawan-tow.cc dans NS-3"
    echo "  3. Compiler NS-3"
}

# Fonction pour vérifier l'environnement
check_environment() {
    echo "Vérification de l'environnement..."

    # Vérifier NS-3
    if [ ! -d "$NS3_PATH" ]; then
        echo "✗ Répertoire NS-3 introuvable: $NS3_PATH"
        echo "Veuillez modifier la variable NS3_PATH dans ce script"
        exit 1
    fi

    if [ ! -f "$NS3_PATH/ns3" ]; then
        echo "✗ Script ns3 introuvable dans $NS3_PATH"
        echo "Assurez-vous que NS-3 est correctement installé"
        exit 1
    fi

    # Vérifier le fichier de simulation
    if [ ! -f "$NS3_PATH/scratch/lorawan-tow.cc" ]; then
        echo "⚠ Fichier lorawan-tow.cc non trouvé dans scratch/"
        echo "Assurez-vous de copier le fichier de simulation dans le répertoire scratch/"
    fi

    echo "✓ Environnement vérifié"
}

# Traitement des arguments
case "$1" in
    --scenario1)
        check_environment
        run_scenario1
        ;;
    --scenario2)
        check_environment
        run_scenario2
        ;;
    --plots)
        generate_plots
        ;;
    --all|"")
        check_environment
        run_scenario1
        run_scenario2
        generate_plots
        ;;
    --help)
        show_help
        exit 0
        ;;
    *)
        echo "Option inconnue: $1"
        show_help
        exit 1
        ;;
esac

echo ""
echo "=== Simulation terminée ==="
echo "Résultats disponibles dans: $SIMULATION_DIR"
echo ""
echo "Fichiers générés:"
ls -la "$SIMULATION_DIR"
