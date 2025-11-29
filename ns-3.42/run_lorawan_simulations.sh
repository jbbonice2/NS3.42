#!/bin/bash

# Script d'automatisation des simulations LoRaWAN
# Exécute les comparaisons d'algorithmes selon différents scénarios

echo "================================================="
echo "  Automated LoRaWAN Algorithm Comparison Suite"
echo "================================================="

# Créer dossier de résultats avec timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="simulation_results_$TIMESTAMP"
mkdir -p "$RESULTS_DIR"

# Initialiser le fichier de résultats principal
RESULTS_FILE="$RESULTS_DIR/results.csv"
echo "nDevices,simTime,obstacles,algorithm,PDR,EC" > "$RESULTS_FILE"

# Copier le fichier de résultats dans le répertoire de travail aussi
cp "$RESULTS_FILE" "results.csv"

# Fonction pour exécuter une simulation avec gestion d'erreurs
run_simulation() {
    local n=$1
    local t=$2
    local obs=$3
    local algo=$4
    
    echo "Running: $algo with $n devices, $t days, obstacles=$obs"
    
    # Calculer le temps en secondes
    local simTime=$((t * 86400))
    
    # Exécuter la simulation
    if ./ns3 run "scratch/lorawan-comparison-working --nDevices=$n --simTime=$simTime --obstacles=$obs --algorithm=$algo"; then
        echo "✓ Success: $algo ($n devices, $t days, obstacles=$obs)"
    else
        echo "✗ Failed: $algo ($n devices, $t days, obstacles=$obs)"
    fi
    
    # Attendre un peu pour éviter les conflits de fichiers
    sleep 1
}

# Fonction pour afficher le progrès
show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    echo "Progress: $current/$total ($percent%)"
}

# Liste des algorithmes à tester
ALGORITHMS=("ADR-MIN" "ADR-MAX" "ADR-AVG" "Q-Learning" "DQN" "DDQN-PER")

echo "Starting simulation suite..."
echo "Algorithms to test: ${ALGORITHMS[@]}"

# Compteur pour le progrès
TOTAL_SIMS=0
CURRENT_SIM=0

# Calculer le nombre total de simulations
# Scénario 1: 10 valeurs de nDevices × 6 algos × 2 environnements = 120
# Scénario 2: 10 valeurs de nDevices × 6 algos × 2 environnements = 120  
# Scénario 3: 7 valeurs de temps × 6 algos × 2 environnements = 84
# Scénario 4: 7 valeurs de temps × 6 algos × 2 environnements = 84
TOTAL_SIMS=408

echo "Total simulations to run: $TOTAL_SIMS"
echo ""

# =============================================================================
# SCÉNARIO 1: Scalabilité en nombre de nœuds (10-100 nœuds, 1 jour)
# =============================================================================
echo "=== SCÉNARIO 1: Node Scalability (10-100 nodes, 1 day) ==="

for n in 10 20 30 40 50 60 70 80 90 100; do
    for obs in false true; do
        for algo in "${ALGORITHMS[@]}"; do
            CURRENT_SIM=$((CURRENT_SIM + 1))
            show_progress $CURRENT_SIM $TOTAL_SIMS
            run_simulation $n 1 $obs "$algo"
        done
    done
done

echo "Scenario 1 completed!"
echo ""

# =============================================================================
# SCÉNARIO 2: Grande scalabilité (100-1000 nœuds, 1 jour)
# =============================================================================
echo "=== SCÉNARIO 2: Large Scale (100-1000 nodes, 1 day) ==="

for n in 100 200 300 400 500 600 700 800 900 1000; do
    for obs in false true; do
        for algo in "${ALGORITHMS[@]}"; do
            CURRENT_SIM=$((CURRENT_SIM + 1))
            show_progress $CURRENT_SIM $TOTAL_SIMS
            run_simulation $n 1 $obs "$algo"
        done
    done
done

echo "Scenario 2 completed!"
echo ""

# =============================================================================
# SCÉNARIO 3: Durée d'apprentissage (100 nœuds, 1-7 jours)
# =============================================================================
echo "=== SCÉNARIO 3: Learning Duration (100 nodes, 1-7 days) ==="

for t in 1 2 3 4 5 6 7; do
    for obs in false true; do
        for algo in "${ALGORITHMS[@]}"; do
            CURRENT_SIM=$((CURRENT_SIM + 1))
            show_progress $CURRENT_SIM $TOTAL_SIMS
            run_simulation 100 $t $obs "$algo"
        done
    done
done

echo "Scenario 3 completed!"
echo ""

# =============================================================================
# SCÉNARIO 4: Apprentissage à grande échelle (1000 nœuds, 1-7 jours)
# =============================================================================
echo "=== SCÉNARIO 4: Large Scale Learning (1000 nodes, 1-7 days) ==="

for t in 1 2 3 4 5 6 7; do
    for obs in false true; do
        for algo in "${ALGORITHMS[@]}"; do
            CURRENT_SIM=$((CURRENT_SIM + 1))
            show_progress $CURRENT_SIM $TOTAL_SIMS
            run_simulation 1000 $t $obs "$algo"
        done
    done
done

echo "Scenario 4 completed!"
echo ""

# =============================================================================
# FINALISATION ET ANALYSE
# =============================================================================

# Copier les résultats finaux
cp "results.csv" "$RESULTS_DIR/"

# Créer un rapport de synthèse
REPORT_FILE="$RESULTS_DIR/simulation_report.txt"
echo "LoRaWAN Algorithm Comparison - Simulation Report" > "$REPORT_FILE"
echo "Generated on: $(date)" >> "$REPORT_FILE"
echo "Total simulations completed: $TOTAL_SIMS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Compter les résultats par algorithme
echo "Results summary by algorithm:" >> "$REPORT_FILE"
for algo in "${ALGORITHMS[@]}"; do
    count=$(grep -c "$algo" "$RESULTS_FILE" 2>/dev/null || echo "0")
    echo "  $algo: $count simulations" >> "$REPORT_FILE"
done

echo "" >> "$REPORT_FILE"
echo "Files generated:" >> "$REPORT_FILE"
echo "  - results.csv: Complete simulation results" >> "$REPORT_FILE"
echo "  - simulation_report.txt: This summary report" >> "$REPORT_FILE"

# Afficher le résumé
echo "================================================="
echo "           SIMULATION SUITE COMPLETED"
echo "================================================="
echo ""
echo "Results directory: $RESULTS_DIR"
echo "Main results file: $RESULTS_DIR/results.csv"
echo "Total simulations: $TOTAL_SIMS"
echo ""

# Afficher un aperçu des résultats
echo "=== Sample Results (first 10 lines) ==="
head -11 "$RESULTS_FILE"

echo ""
echo "=== Results Summary by Algorithm ==="
for algo in "${ALGORITHMS[@]}"; do
    count=$(grep -c "$algo" "$RESULTS_FILE" 2>/dev/null || echo "0")
    avg_pdr=$(grep "$algo" "$RESULTS_FILE" 2>/dev/null | awk -F',' '{sum+=$5; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
    avg_energy=$(grep "$algo" "$RESULTS_FILE" 2>/dev/null | awk -F',' '{sum+=$6; count++} END {if(count>0) printf "%.4f", sum/count; else print "N/A"}')
    echo "  $algo: $count sims, Avg PDR: $avg_pdr%, Avg Energy: $avg_energy J"
done

echo ""
echo "For detailed analysis, use:"
echo "  python3 analyze_results.py $RESULTS_DIR/results.csv"
echo "  or open the CSV file in your preferred analysis tool"
echo ""
echo "Simulation suite completed successfully!"
