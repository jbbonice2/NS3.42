#!/bin/bash

# Script d'expérimentation LoRaWAN MAB simplifiée
# Exécute quelques scénarios de test pour valider le fonctionnement

echo "=== Expérimentation LoRaWAN MAB - Version Simplifiée ==="

# Créer le dossier de résultats
mkdir -p lorawan_results

# Scénarios de test réduits
SCENARIOS=(0 1)  # 0: SF_ONLY, 1: JOINT_CH_SF
MAB_MODES=(0 1 4)  # 0: combinatorial, 1: independent, 4: random
DEVICES=(3 9)  # Nombre de devices réduit pour tests rapides
TX_INTERVAL=20

echo "Lancement des expériences..."

for scenario in "${SCENARIOS[@]}"; do
    for mab_mode in "${MAB_MODES[@]}"; do
        for devices in "${DEVICES[@]}"; do
            
            # Noms pour les modes
            case $mab_mode in
                0) mode_name="COMBINATORIAL" ;;
                1) mode_name="INDEPENDENT" ;;
                4) mode_name="RANDOM" ;;
            esac
            
            case $scenario in
                0) scenario_name="SF_ONLY" ;;
                1) scenario_name="JOINT_CH_SF" ;;
            esac
            
            result_file="lorawan_results/res_${scenario_name}_MAB_${mode_name}_${devices}dev_${TX_INTERVAL}s.csv"
            
            echo "Exécution: Scénario $scenario_name, Mode $mode_name, $devices devices"
            
            # Exécuter l'expérience
            timeout 60s ./ns3 run "scratch/lorawan-sensors-optimization --scenario=$scenario --mabMode=$mab_mode --numDevices=$devices --txInterval=$TX_INTERVAL --numTrials=50 --csvOut=$result_file" > /dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                echo "  ✓ Terminé avec succès"
            else
                echo "  ✗ Échec ou timeout"
            fi
            
            # Petite pause entre les expériences
            sleep 1
        done
    done
done

echo ""
echo "=== Expériences Terminées ==="
echo "Fichiers de résultats:"
ls -la lorawan_results/

echo ""
echo "Lancement de l'analyse des résultats..."
python3 analyze_lorawan_mab_results.py
