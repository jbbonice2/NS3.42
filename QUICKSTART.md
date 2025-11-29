# Guide de Démarrage Rapide - LoRaWAN Simulation

## 🚀 Installation et Configuration

### 1. Vérification de l'environnement
```bash
# Vérifier les dépendances et l'environnement
python3 check_environment.py
```

### 2. Installation des dépendances
```bash
# Installation automatique
pip install -r requirements.txt

# Ou installation manuelle
pip install pandas matplotlib seaborn numpy
```

### 3. Test des scripts de visualisation
```bash
# Tester avec des données simulées
python3 test_visualization.py
```

## 📊 Exécution Complète

### Option 1: Script automatisé (recommandé)
```bash
# Tout en une fois
./run_simulation.sh all

# Ou étape par étape
./run_simulation.sh compile
./run_simulation.sh run
./run_simulation.sh plot
```

### Option 2: Exécution manuelle
```bash
# 1. Compilation
cd ns-3.42
./ns3 configure --enable-examples --enable-tests
./ns3 build

# 2. Simulation
./ns3 run lorawan-logistics-mab-mixed-interf

# 3. Visualisation
cd ..
python ns-3.42/plot_lorawan_mixed_interf.py lorawan_mixed_results_interf/
```

## 📈 Résultats et Graphiques

### Dossiers générés
- `lorawan_mixed_results_interf/` - Résultats CSV
- `lorawan_mixed_results_interf/lorawan-logistics-mab-mixed_ALL_plots/` - Graphiques

### Types de graphiques
- **Taux de succès** par paramètres LoRa
- **Métriques temporelles** (RSSI, SNR, énergie)
- **Analyses par dispositif** (PDR, efficacité)
- **Heatmaps** de performance
- **Comparaisons** entre configurations

## 🔧 Personnalisation

### Modifier les paramètres de simulation
Éditez `lorawan-logistics-mab-mixed-interf.cc` (lignes ~160-205):
- Nombre de dispositifs
- Paramètres LoRa (SF, puissance, payload)
- Durée de simulation

### Ajouter des graphiques
Modifiez `plot_lorawan_mixed_interf.py`:
- Nouvelles métriques
- Styles de visualisation
- Analyses personnalisées

## 🐛 Dépannage

### Problèmes courants
```bash
# Vérification complète
python3 check_environment.py

# Nettoyer et recompiler
cd ns-3.42
./ns3 clean
./ns3 build

# Vérifier les fichiers générés
ls -la lorawan_mixed_results_interf/
```

### Support
- Documentation complète: `README.md`
- Scripts de visualisation: `ns-3.42/scratch/README_plots.md`
- Configuration: `config.ini`

## 📚 Fichiers Utiles

- `requirements.txt` - Dépendances Python
- `run_simulation.sh` - Script d'automation
- `check_environment.py` - Vérification environnement
- `test_visualization.py` - Test des scripts
- `config.ini` - Configuration simulation

---

**Commande unique pour démarrer:**
```bash
./run_simulation.sh all
```
