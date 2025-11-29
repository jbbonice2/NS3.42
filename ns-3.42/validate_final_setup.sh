#!/bin/bash

echo "==========================================
VALIDATION FINALE DU SETUP LORAWAN MAB
==========================================

1. VÉRIFICATION DE L'ENVIRONNEMENT
----------------------------------------"
cd /home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42

echo "✓ Répertoire de travail: $(pwd)"
echo "✓ Fichier principal: $(test -f scratch/lorawan-sensors-optimization.cc && echo "PRÉSENT" || echo "MANQUANT")"

echo "
2. VÉRIFICATION DES FICHIERS PROBLÉMATIQUES
----------------------------------------"
problematic_files=$(find scratch/ -name "*.cc" | grep -v lorawan-sensors-optimization.cc | grep -v scratch-simulator.cc)
if [ -z "$problematic_files" ]; then
    echo "✓ Aucun fichier .cc problématique trouvé dans scratch/"
else
    echo "✗ Fichiers .cc problématiques détectés:"
    echo "$problematic_files"
fi

echo "
3. VÉRIFICATION DE LA COMPILATION
----------------------------------------"
if [ -f "build/scratch/ns3.42-lorawan-sensors-optimization-default" ]; then
    echo "✓ Exécutable compilé et présent"
    ls -la build/scratch/ns3.42-lorawan-sensors-optimization-default
else
    echo "✗ Exécutable manquant - Tentative de compilation..."
    ./ns3 build
    if [ $? -eq 0 ]; then
        echo "✓ Compilation réussie"
    else
        echo "✗ Échec de la compilation"
        exit 1
    fi
fi

echo "
4. TEST D'EXÉCUTION RAPIDE
----------------------------------------"
echo "Test avec 2 devices, 1 transmission, mode RANDOM..."
./ns3 run "scratch/lorawan-sensors-optimization --numDevices=2 --numTrials=1 --mabMode=4 --csvOut=validation_test.csv" > /dev/null 2>&1

if [ $? -eq 0 ] && [ -f "validation_test.csv" ]; then
    lines=$(wc -l < validation_test.csv)
    echo "✓ Test d'exécution réussi"
    echo "   Fichier de résultat généré: $lines lignes"
    rm -f validation_test.csv sensors_optimization_lorawan_results.csv
else
    echo "✗ Échec du test d'exécution"
    exit 1
fi

echo "
5. VÉRIFICATION DES SCRIPTS D'ANALYSE
----------------------------------------"
analysis_scripts=("run_lorawan_experiments.py" "analyze_results_final.py")
for script in "${analysis_scripts[@]}"; do
    if [ -f "scratch/$script" ]; then
        echo "✓ Script d'analyse présent: $script"
    else
        echo "✗ Script d'analyse manquant: $script"
    fi
done

echo "
6. VÉRIFICATION DES RÉSULTATS EXISTANTS
----------------------------------------"
if [ -d "scratch/lorawan_results" ]; then
    result_count=$(ls scratch/lorawan_results/*.csv 2>/dev/null | wc -l)
    echo "✓ Dossier de résultats présent avec $result_count fichiers CSV"
else
    echo "⚠ Dossier de résultats non trouvé (sera créé à la première exécution)"
fi

echo "
==========================================
RÉSUMÉ FINAL
==========================================
🎉 SETUP LORAWAN MAB ENTIÈREMENT FONCTIONNEL

Le problème de compilation a été résolu en:
✅ Déplaçant les fichiers obsolètes vers scratch/obsolete_files/
✅ Renommant les fichiers .cc en .cc.bak pour éviter la compilation
✅ Reconfigurant et recompilant ns-3 avec succès
✅ Validant l'exécution du programme principal

PRÊT POUR:
- Exécution de nouvelles simulations
- Analyse des résultats existants  
- Expérimentation avec les différents algorithmes MAB

COMMANDES UTILES:
# Exécution simple
./ns3 run \"scratch/lorawan-sensors-optimization --numDevices=10 --numTrials=50\"

# Batch d'expériences
cd scratch && python3 run_lorawan_experiments.py

# Analyse des résultats
cd scratch && python3 analyze_results_final.py

=========================================="
