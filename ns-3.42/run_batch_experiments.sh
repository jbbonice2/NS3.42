#!/bin/bash

# Script de batch d'expériences LoRaWAN MAB
echo "=== Batch d'Expériences LoRaWAN MAB ==="

cd /home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42

# Créer le dossier de résultats
mkdir -p lorawan_results

# Fonctions utilitaires
run_experiment() {
    local scenario=$1
    local mab_mode=$2
    local devices=$3
    local interval=$4
    local trials=$5
    local output_file=$6
    
    echo "  Exécution: Scénario $scenario, Mode $mab_mode, $devices devices..."
    
    ./ns3 run "scratch/lorawan-sensors-optimization --scenario=$scenario --mabMode=$mab_mode --numDevices=$devices --txInterval=$interval --numTrials=$trials --csvOut=$output_file" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "    ✓ Succès"
        return 0
    else
        echo "    ✗ Échec"
        return 1
    fi
}

# Expériences de base
echo "1. Test des algorithmes de base..."

# Scénario SF_ONLY
run_experiment 0 0 3 20 30 "lorawan_results/sf_only_combinatorial_3dev.csv"
run_experiment 0 1 3 20 30 "lorawan_results/sf_only_independent_3dev.csv"
run_experiment 0 4 3 20 30 "lorawan_results/sf_only_random_3dev.csv"

# Scénario JOINT
run_experiment 1 0 3 20 30 "lorawan_results/joint_combinatorial_3dev.csv"
run_experiment 1 1 3 20 30 "lorawan_results/joint_independent_3dev.csv"
run_experiment 1 4 3 20 30 "lorawan_results/joint_random_3dev.csv"

echo ""
echo "2. Test avec plus de devices..."

# Tests avec plus de devices
run_experiment 0 0 6 20 25 "lorawan_results/sf_only_combinatorial_6dev.csv"
run_experiment 1 0 6 20 25 "lorawan_results/joint_combinatorial_6dev.csv"
run_experiment 1 4 6 20 25 "lorawan_results/joint_random_6dev.csv"

echo ""
echo "3. Test avec différents intervalles..."

# Tests avec différents intervalles
run_experiment 1 0 3 10 20 "lorawan_results/joint_combinatorial_3dev_10s.csv"
run_experiment 1 0 3 40 20 "lorawan_results/joint_combinatorial_3dev_40s.csv"

echo ""
echo "=== Résultats des Expériences ==="
echo "Fichiers générés:"
ls -la lorawan_results/

echo ""
echo "Analyse des résultats..."
python3 analyze_lorawan_mab_results.py
