# Guide d'exécution rapide - Simulations LoRaWAN

## 🚀 Exécution rapide

### Option 1: Tout automatiquement
```bash
chmod +x run_simulation.sh
./run_simulation.sh all
```

### Option 2: Étape par étape
```bash
./run_simulation.sh compile     # Compilation
./run_simulation.sh run-all     # Toutes les simulations
./run_simulation.sh plot-all    # Tous les graphiques
./run_simulation.sh summary     # Résumé des résultats
```

## 📋 Liste des simulations

| Simulation | Commande | Dossier résultats | Script visualisation |
|------------|----------|------------------|---------------------|
| **Statique** | `./ns3 run lorawan-logistics-mab-static` | `lorawan_static_results/` | `plot_lorawan_static.py` |
| **Statique + Interf** | `./ns3 run lorawan-logistics-mab-static-interf` | `lorawan_static_results_interf/` | `plot_lorawan_static.py` |
| **Mobile** | `./ns3 run lorawan-logistics-mab-mobile` | `lorawan_mobile_results/` | `plot_lorawan_mobile.py` |
| **Mobile + Interf** | `./ns3 run lorawan-logistics-mab-mobile-interf` | `lorawan_mobile_results_interf/` | `plot_lorawan_mobile.py` |
| **Mixte** | `./ns3 run lorawan-logistics-mab-mixed` | `lorawan_mixed_results/` | `plot_lorawan_mixed.py` |
| **Mixte + Interf** | `./ns3 run lorawan-logistics-mab-mixed-interf` | `lorawan_mixed_results_interf/` | `plot_lorawan_mixed.py` |

## 📊 Génération des graphiques

```bash
# Simulations statiques
python3 ns-3.42/scratch/plot_lorawan_static.py lorawan_static_results/
python3 ns-3.42/scratch/plot_lorawan_static.py lorawan_static_results_interf/

# Simulations mobiles
python3 ns-3.42/scratch/plot_lorawan_mobile.py lorawan_mobile_results/
python3 ns-3.42/scratch/plot_lorawan_mobile.py lorawan_mobile_results_interf/

# Simulations mixtes
python3 ns-3.42/scratch/plot_lorawan_mixed.py lorawan_mixed_results/
python3 ns-3.42/scratch/plot_lorawan_mixed.py lorawan_mixed_results_interf/
```

## 🔍 Vérification

```bash
# Vérifier l'environnement
python3 check_environment.py

# Tester les scripts de visualisation
python3 test_visualization.py

# Résumé des résultats
./run_simulation.sh summary
```

## 📁 Structure des résultats

```
lorawan_[type]_results[_interf]/
├── *.csv                    # Données de simulation
└── plots/
    ├── success_rate_*.png   # Taux de succès
    ├── rssi_*.png          # Métriques RSSI
    ├── snr_*.png           # Métriques SNR
    ├── energy_*.png        # Consommation énergétique
    ├── distance_*.png      # Analyses de distance
    ├── interference_*.png  # Analyses d'interférence
    └── simulation_report.txt # Rapport détaillé
```

## ⚡ Commandes utiles

```bash
# Compilation rapide
cd ns-3.42 && ./ns3 build

# Exécution d'une simulation spécifique
./ns3 run lorawan-logistics-mab-mixed-interf

# Graphiques pour une simulation spécifique
python3 ns-3.42/scratch/plot_lorawan_mixed.py lorawan_mixed_results_interf/

# Nettoyer et recompiler
cd ns-3.42 && ./ns3 clean && ./ns3 build
```

## 🐛 Dépannage

```bash
# Problèmes de compilation
cd ns-3.42 && ./ns3 clean && ./ns3 configure --enable-examples --enable-tests && ./ns3 build

# Problèmes Python
pip install -r requirements.txt

# Vérifier les résultats
ls -la lorawan_*_results*/
```

---

Pour plus de détails, consultez le fichier `README.md` complet.
