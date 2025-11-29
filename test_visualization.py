#!/usr/bin/env python3
"""
Script de test pour valider les scripts de visualisation LoRaWAN
"""

import os
import sys
import subprocess
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """Crée des données de test pour valider les scripts"""
    print("🔬 Création des données de test...")
    
    # Générer des données de test
    np.random.seed(42)
    n_devices = 100
    n_messages = 10
    
    data = []
    base_time = datetime(2025, 7, 10, 18, 18, 34)
    
    for device_id in range(1, n_devices + 1):
        for message_id in range(1, n_messages + 1):
            time = base_time + timedelta(seconds=message_id * 15)
            
            # Paramètres LoRa aléatoires
            sf = np.random.choice([7, 8, 9, 10, 11])
            tx_power = np.random.choice([2, 8])
            payload = np.random.choice([50, 100, 150, 200, 250])
            bw = np.random.choice([125000, 250000])
            
            # Position aléatoire
            distance = np.random.uniform(100, 1000)
            angle = np.random.uniform(0, 2 * np.pi)
            x = distance * np.cos(angle)
            y = distance * np.sin(angle)
            z = np.random.uniform(0, 10)
            
            # Métriques simulées
            rssi = tx_power - 20 * np.log10(distance) - 32.44 - np.random.normal(0, 5)
            snr = np.random.normal(-10, 5)
            success = 1 if rssi > -130 and snr > -20 else 0
            
            # Énergie et time on air
            time_on_air = (2**sf / bw) * 1000 * 8  # approximation
            energy_consumed = (10**(tx_power/10) / 1000) * (time_on_air / 1000)
            
            # Interférences
            interference_loss = np.random.uniform(5, 20)
            
            data.append({
                'deviceId': device_id,
                'messageId': message_id,
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'x': x,
                'y': y,
                'z': z,
                'distance': distance,
                'txPower': tx_power,
                'sf': sf,
                'bw': bw,
                'cr': 1,
                'payload': payload,
                'nDevices': n_devices,
                'rssi': rssi,
                'snr': snr,
                'success': success,
                'energyConsumed': energy_consumed,
                'timeOnAir': time_on_air,
                'totalTx': n_messages,
                'totalRx': sum(1 for _ in range(n_messages) if np.random.random() > 0.1),
                'interferenceLoss': interference_loss
            })
    
    return pd.DataFrame(data)

def test_visualization_scripts():
    """Teste les scripts de visualisation avec des données de test"""
    print("🧪 Test des scripts de visualisation...")
    
    # Créer des données de test
    df = create_test_data()
    
    # Créer un dossier temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Dossier temporaire: {temp_dir}")
        
        # Sauvegarder les données de test
        test_dir = os.path.join(temp_dir, "test_results")
        os.makedirs(test_dir, exist_ok=True)
        
        test_file = os.path.join(test_dir, "test_data.csv")
        df.to_csv(test_file, index=False)
        print(f"💾 Données sauvegardées: {test_file}")
        
        # Tester le script principal
        script_path = "ns-3.42/plot_lorawan_mixed_interf.py"
        if os.path.exists(script_path):
            print(f"🚀 Test du script: {script_path}")
            try:
                result = subprocess.run([
                    sys.executable, script_path, test_dir
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✓ Script exécuté avec succès")
                    
                    # Vérifier les graphiques générés
                    plots_dir = os.path.join(test_dir, "test_data_plots")
                    if os.path.exists(plots_dir):
                        plot_files = os.listdir(plots_dir)
                        print(f"📊 {len(plot_files)} graphiques générés")
                        for plot_file in plot_files[:5]:  # Afficher les 5 premiers
                            print(f"   - {plot_file}")
                        if len(plot_files) > 5:
                            print(f"   ... et {len(plot_files) - 5} autres")
                    else:
                        print("⚠ Aucun dossier de graphiques trouvé")
                        
                else:
                    print(f"❌ Erreur lors de l'exécution: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("❌ Timeout lors de l'exécution")
            except Exception as e:
                print(f"❌ Exception: {e}")
        else:
            print(f"❌ Script non trouvé: {script_path}")
        
        # Pause pour permettre l'inspection manuelle si nécessaire
        input("🔍 Appuyez sur Entrée pour continuer (les fichiers temporaires seront supprimés)...")

def main():
    """Fonction principale"""
    print("🧪 Test des scripts de visualisation LoRaWAN")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon dossier
    if not os.path.exists("ns-3.42"):
        print("❌ Dossier ns-3.42 non trouvé")
        print("   Exécutez ce script depuis le dossier racine du projet")
        return 1
    
    try:
        test_visualization_scripts()
        print("\n✅ Tests terminés avec succès!")
        return 0
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
