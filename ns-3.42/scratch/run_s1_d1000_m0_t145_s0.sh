#!/bin/bash

# Script d'automatisation pour les simulations LoRaWAN ADR - Scénario 1
# Configuration: D=1000, M=0, T=145, S=0
# Fichier: run_s1_d1000_m0_t145_s0.sh

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCENARIO=1

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Simulation LoRaWAN ADR - Scénario $SCENARIO${NC}"
echo -e "${GREEN}  D=1000, M=0, T=145, S=0${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration du simulateur NS-3
NS3_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
SIMULATION_NAME="lorawan-adr-simulationfinal"

NUM_RUNS=100
MAX_MESSAGES=110

RESULTS_DIR="$NS3_DIR/resultsfinal"
RESULTS_SUMMARIES_DIR="$RESULTS_DIR/summaries"
mkdir -p "$RESULTS_SUMMARIES_DIR"

scenarioName="density"
SCENARIO_SUMMARY_DIR="$RESULTS_SUMMARIES_DIR/$scenarioName"
mkdir -p "$SCENARIO_SUMMARY_DIR"

ADR_ALGOS=("No-ADR" "ADR-MAX" "ADR-AVG" "ADR-Lite")

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  SCENARIO 1: Variation de la densité${NC}"
echo -e "${BLUE}========================================${NC}"

DENSITIES=(1000)
MOBILITIES_S1=(0)
TRAFFIC_INTERVALS_S1=(145)
SIGMAS_S1=(0)

total_configs=$((${#DENSITIES[@]} * ${#MOBILITIES_S1[@]} * ${#TRAFFIC_INTERVALS_S1[@]} * ${#SIGMAS_S1[@]} * ${#ADR_ALGOS[@]} * NUM_RUNS))
current_config=0

echo -e "${YELLOW}Total configurations: $total_configs${NC}"

for density in "${DENSITIES[@]}"; do
    for mobility in "${MOBILITIES_S1[@]}"; do
        for traffic in "${TRAFFIC_INTERVALS_S1[@]}"; do
            for sigma in "${SIGMAS_S1[@]}"; do
                for run in $(seq 1 $NUM_RUNS); do
                    for adr_algo in "${ADR_ALGOS[@]}"; do
                        current_config=$((current_config + 1))
                        progress=$(awk "BEGIN {printf \"%.2f\", ($current_config/$total_configs)*100}")
                        
                        echo -e "${GREEN}[S1: $progress%] Running: Density=$density, Mobility=$mobility km/h, Traffic=$traffic s, Sigma=$sigma, ADR=$adr_algo, Run=$run/$NUM_RUNS${NC}"
                        
                        cd "$NS3_DIR"
                        simTime=$(awk -v m="$MAX_MESSAGES" -v t="$traffic" 'BEGIN{printf "%.0f", m*t + 60}')
                        ./ns3 run "$SIMULATION_NAME --scenario=$SCENARIO --numDevices=$density --mobilitySpeed=$mobility --trafficInterval=$traffic --sigma=$sigma --adrAlgo=$adr_algo --maxMessages=$MAX_MESSAGES --runNumber=$run --simulationTime=$simTime" 2>&1 | tee -a "$RESULTS_DIR/simulations.log"
                        
                        if [ $? -ne 0 ]; then
                            echo -e "${RED}Error in simulation!${NC}"
                        fi
                    done
                done
            done
        done
    done
done

echo -e "${GREEN}Scenario 1 completed!${NC}"

# Aggregation
echo -e "\n${BLUE}Aggregating results...${NC}"

aggregate_by_run() {
    for runnum in $(seq 1 $NUM_RUNS); do
        files=("$SCENARIO_SUMMARY_DIR"/summary_scen${SCENARIO}_*"_run${runnum}.csv")
        if [ ! -e "${files[0]}" ]; then
            continue
        fi

        outFile="$SCENARIO_SUMMARY_DIR/summary_${scenarioName}_run${runnum}.csv"
        header=$(head -n1 "${files[0]}" 2>/dev/null || echo "")
        if [ -z "$header" ]; then
            continue
        fi
        echo "$header,alg,scenario" > "$outFile"

        for f in "${files[@]}"; do
            base=$(basename "$f")
            alg=$(echo "$base" | sed -n 's/.*_\(No-ADR\|ADR-MAX\|ADR-AVG\|ADR-Lite\)_run[0-9]\+\.csv/\1/p')
            if [ -z "$alg" ]; then
                alg="$(basename "$f" .csv)"
            fi
            tail -n +2 "$f" | awk -v alg="$alg" -v scen="$scenarioName" 'BEGIN{OFS=","} {print $0,alg,scen}' >> "$outFile"
        done

        echo -e "${GREEN}Created per-run aggregated file: $outFile${NC}"
    done
}

aggregate_by_run

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  SIMULATION SCÉNARIO $SCENARIO TERMINÉE!${NC}"
echo -e "${GREEN}========================================${NC}"

num_files=$(ls -1 "$SCENARIO_SUMMARY_DIR"/summary_${scenarioName}_*.csv 2>/dev/null | wc -l)
echo -e "${GREEN}Fichiers générés: $num_files${NC}"
