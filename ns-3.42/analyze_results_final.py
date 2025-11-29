#!/usr/bin/env python3
"""
Script simple d'analyse des résultats LoRaWAN MAB
Génère des statistiques textuelles et des graphiques sauvegardés
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

def parse_filename(filename):
    """Parse le nom de fichier pour extraire les paramètres expérimentaux"""
    try:
        parts = filename.replace('.csv', '').split('_')
        
        if filename.startswith("res_"):
            if "SF_ONLY" in filename:
                scenario = "SF_ONLY"
                if "MAB_COMBINATORIAL" in filename:
                    mab_mode = "MAB_COMBINATORIAL"
                elif "MAB_INDEPENDENT" in filename:
                    mab_mode = "MAB_INDEPENDENT"
                elif "MAB_RANDOM" in filename:
                    mab_mode = "MAB_RANDOM"
                else:
                    mab_mode = "UNKNOWN"
            elif "JOINT_CH_SF" in filename:
                scenario = "JOINT_CH_SF"
                if "MAB_COMBINATORIAL" in filename:
                    mab_mode = "MAB_COMBINATORIAL"
                elif "MAB_INDEPENDENT" in filename:
                    mab_mode = "MAB_INDEPENDENT"
                elif "MAB_RANDOM" in filename:
                    mab_mode = "MAB_RANDOM"
                else:
                    mab_mode = "UNKNOWN"
            else:
                scenario = "UNKNOWN"
                mab_mode = "UNKNOWN"
            
            # Extraire le nombre de devices
            devices = 3
            for part in parts:
                if 'dev' in part and part != 'devices':
                    try:
                        devices = int(part.replace('dev', ''))
                    except:
                        pass
            
            interval = 20
            for part in parts:
                if 's' in part and part != 'devices':
                    try:
                        interval = int(part.replace('s', ''))
                    except:
                        pass
                        
        else:
            # Autres formats
            if 'sf_only' in filename.lower():
                scenario = "SF_ONLY"
            elif 'joint' in filename.lower():
                scenario = "JOINT_CH_SF"
            else:
                scenario = "UNKNOWN"
            
            if 'combinatorial' in filename.lower():
                mab_mode = "MAB_COMBINATORIAL"
            elif 'independent' in filename.lower():
                mab_mode = "MAB_INDEPENDENT"
            elif 'random' in filename.lower():
                mab_mode = "MAB_RANDOM"
            else:
                mab_mode = "UNKNOWN"
            
            devices = 3
            interval = 20
            
        return scenario, mab_mode, devices, interval
    except Exception as e:
        print(f"Erreur parsing filename {filename}: {e}")
        return "UNKNOWN", "UNKNOWN", 3, 20

def load_and_analyze():
    """Charger et analyser tous les fichiers de résultats"""
    results_dir = '/home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42/lorawan_results/'
    
    if not os.path.exists(results_dir):
        print(f"Dossier de résultats non trouvé: {results_dir}")
        return None
    
    result_files = glob.glob(os.path.join(results_dir, "*.csv"))
    
    if not result_files:
        print("Aucun fichier de résultats trouvé")
        return None
    
    print(f"Analyse de {len(result_files)} fichiers de résultats...")
    print("=" * 80)
    
    all_results = []
    
    for file_path in result_files:
        try:
            filename = os.path.basename(file_path)
            print(f"\nTraitement de: {filename}")
            
            scenario, mab_mode, num_devices, tx_interval = parse_filename(filename)
            
            if scenario == "UNKNOWN" or mab_mode == "UNKNOWN":
                print(f"  Paramètres non reconnus, fichier ignoré")
                continue
            
            print(f"  Scénario: {scenario}")
            print(f"  Mode MAB: {mab_mode}")
            print(f"  Devices: {num_devices}")
            print(f"  Intervalle: {tx_interval}s")
            
            # Charger le fichier CSV
            df = pd.read_csv(file_path)
            
            if df.empty:
                print(f"  Fichier vide, ignoré")
                continue
            
            print(f"  Transmissions totales: {len(df)}")
            
            # Calculer les métriques
            total_transmissions = len(df)
            successful_transmissions = len(df[df['ack'] == 1])
            fsr = successful_transmissions / total_transmissions if total_transmissions > 0 else 0.0
            
            print(f"  Transmissions réussies: {successful_transmissions}")
            print(f"  FSR: {fsr:.4f}")
            
            # Diversité SF
            unique_sfs = df['sf'].unique()
            sf_diversity = len(unique_sfs)
            print(f"  SFs utilisés: {sorted(unique_sfs)}")
            print(f"  Diversité SF: {sf_diversity}")
            
            # Diversité canaux
            if 'channel' in df.columns:
                unique_channels = df['channel'].unique()
                channel_diversity = len(unique_channels)
                print(f"  Canaux utilisés: {sorted(unique_channels)}")
                print(f"  Diversité canaux: {channel_diversity}")
            else:
                channel_diversity = 1
                print(f"  Diversité canaux: 1 (colonne channel non trouvée)")
            
            # Statistiques par device
            device_stats = []
            print(f"  Statistiques par device:")
            for device_id in sorted(df['deviceId'].unique()):
                device_data = df[df['deviceId'] == device_id]
                device_total = len(device_data)
                device_success = len(device_data[device_data['ack'] == 1])
                device_fsr = device_success / device_total if device_total > 0 else 0.0
                device_stats.append(device_fsr)
                print(f"    Device {device_id}: {device_fsr:.4f} ({device_success}/{device_total})")
            
            # Fairness (Jain's Fairness Index)
            if len(device_stats) > 1:
                sum_rates = sum(device_stats)
                sum_squares = sum(x**2 for x in device_stats)
                fairness_jain = (sum_rates**2) / (len(device_stats) * sum_squares) if sum_squares > 0 else 0.0
                fairness_std = 1.0 - np.std(device_stats)
            else:
                fairness_jain = 1.0
                fairness_std = 1.0
            
            print(f"  Fairness (Jain): {fairness_jain:.4f}")
            print(f"  Fairness (1-std): {fairness_std:.4f}")
            
            # Distribution des SF
            sf_counts = df['sf'].value_counts().sort_index()
            print(f"  Distribution SF: {dict(sf_counts)}")
            
            result = {
                'scenario': scenario,
                'mab_mode': mab_mode,
                'num_devices': num_devices,
                'tx_interval': tx_interval,
                'fsr': fsr,
                'fairness_jain': fairness_jain,
                'fairness_std': fairness_std,
                'sf_diversity': sf_diversity,
                'channel_diversity': channel_diversity,
                'total_transmissions': total_transmissions,
                'successful_transmissions': successful_transmissions,
                'sf_distribution': dict(sf_counts)
            }
            
            all_results.append(result)
            print(f"  ✓ Ajouté aux résultats")
            
        except Exception as e:
            print(f"  ✗ Erreur lors du traitement: {e}")
            continue
    
    if not all_results:
        print("\nAucun résultat valide trouvé")
        return None
    
    return pd.DataFrame(all_results)

def create_summary_plots(df):
    """Créer des graphiques de synthèse"""
    
    # Configuration matplotlib pour sauvegarder les images
    plt.style.use('default')
    
    # 1. Graphique FSR par mode MAB
    plt.figure(figsize=(12, 8))
    
    modes = df['mab_mode'].unique()
    scenarios = df['scenario'].unique()
    
    x = np.arange(len(modes))
    width = 0.35
    
    for i, scenario in enumerate(scenarios):
        fsr_values = []
        for mode in modes:
            subset = df[(df['mab_mode'] == mode) & (df['scenario'] == scenario)]
            avg_fsr = subset['fsr'].mean() if not subset.empty else 0.0
            fsr_values.append(avg_fsr)
        
        plt.bar(x + i*width, fsr_values, width, label=scenario, alpha=0.8)
    
    plt.xlabel('Mode MAB')
    plt.ylabel('Frame Success Rate (FSR)')
    plt.title('Comparaison FSR par Mode MAB et Scénario')
    plt.xticks(x + width/2, modes, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('lorawan_fsr_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Graphique Fairness
    plt.figure(figsize=(12, 8))
    
    for i, scenario in enumerate(scenarios):
        fairness_values = []
        for mode in modes:
            subset = df[(df['mab_mode'] == mode) & (df['scenario'] == scenario)]
            avg_fairness = subset['fairness_jain'].mean() if not subset.empty else 0.0
            fairness_values.append(avg_fairness)
        
        plt.bar(x + i*width, fairness_values, width, label=scenario, alpha=0.8)
    
    plt.xlabel('Mode MAB')
    plt.ylabel('Fairness Index (Jain)')
    plt.title('Comparaison Fairness par Mode MAB et Scénario')
    plt.xticks(x + width/2, modes, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('lorawan_fairness_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Scaling avec le nombre de devices
    plt.figure(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    markers = ['o', 's', '^', 'D', 'v']
    
    for i, mode in enumerate(modes):
        for j, scenario in enumerate(scenarios):
            subset = df[(df['mab_mode'] == mode) & (df['scenario'] == scenario)]
            if not subset.empty:
                devices = subset['num_devices'].values
                fsr_values = subset['fsr'].values
                plt.plot(devices, fsr_values, 
                        color=colors[i % len(colors)], 
                        marker=markers[j % len(markers)],
                        label=f'{mode}-{scenario}', 
                        linewidth=2, markersize=8, alpha=0.8)
    
    plt.xlabel('Nombre de Devices')
    plt.ylabel('Frame Success Rate (FSR)')
    plt.title('Evolution FSR avec le Nombre de Devices')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('lorawan_scaling_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_detailed_report(df):
    """Générer un rapport détaillé"""
    
    report_lines = []
    report_lines.append("# RAPPORT D'ANALYSE LORAWAN MAB")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    report_lines.append(f"**Nombre d'expériences analysées**: {len(df)}")
    report_lines.append(f"**Scénarios testés**: {', '.join(sorted(df['scenario'].unique()))}")
    report_lines.append(f"**Modes MAB testés**: {', '.join(sorted(df['mab_mode'].unique()))}")
    report_lines.append(f"**Tailles de réseau**: {sorted(df['num_devices'].unique())}")
    report_lines.append("")
    
    report_lines.append("## PERFORMANCES MOYENNES PAR MODE MAB")
    report_lines.append("-" * 50)
    report_lines.append("")
    
    for mode in sorted(df['mab_mode'].unique()):
        mode_data = df[df['mab_mode'] == mode]
        report_lines.append(f"### {mode}")
        report_lines.append(f"- FSR moyen: {mode_data['fsr'].mean():.4f} (±{mode_data['fsr'].std():.4f})")
        report_lines.append(f"- Fairness moyen: {mode_data['fairness_jain'].mean():.4f} (±{mode_data['fairness_jain'].std():.4f})")
        report_lines.append(f"- Diversité SF moyenne: {mode_data['sf_diversity'].mean():.2f}")
        report_lines.append(f"- Nombre d'expériences: {len(mode_data)}")
        report_lines.append("")
    
    report_lines.append("## COMPARAISON SCÉNARIOS")
    report_lines.append("-" * 50)
    report_lines.append("")
    
    for scenario in sorted(df['scenario'].unique()):
        scenario_data = df[df['scenario'] == scenario]
        report_lines.append(f"### {scenario}")
        report_lines.append(f"- FSR moyen: {scenario_data['fsr'].mean():.4f}")
        report_lines.append(f"- Fairness moyen: {scenario_data['fairness_jain'].mean():.4f}")
        report_lines.append(f"- Diversité SF moyenne: {scenario_data['sf_diversity'].mean():.2f}")
        report_lines.append("")
    
    # Meilleures configurations
    best_fsr = df.loc[df['fsr'].idxmax()]
    best_fairness = df.loc[df['fairness_jain'].idxmax()]
    best_sf_diversity = df.loc[df['sf_diversity'].idxmax()]
    
    report_lines.append("## MEILLEURES CONFIGURATIONS")
    report_lines.append("-" * 50)
    report_lines.append("")
    report_lines.append(f"**Meilleure FSR**: {best_fsr['fsr']:.4f}")
    report_lines.append(f"  Mode: {best_fsr['mab_mode']}, Scénario: {best_fsr['scenario']}, Devices: {best_fsr['num_devices']}")
    report_lines.append("")
    report_lines.append(f"**Meilleure Fairness**: {best_fairness['fairness_jain']:.4f}")
    report_lines.append(f"  Mode: {best_fairness['mab_mode']}, Scénario: {best_fairness['scenario']}, Devices: {best_fairness['num_devices']}")
    report_lines.append("")
    report_lines.append(f"**Meilleure Diversité SF**: {best_sf_diversity['sf_diversity']}")
    report_lines.append(f"  Mode: {best_sf_diversity['mab_mode']}, Scénario: {best_sf_diversity['scenario']}, Devices: {best_sf_diversity['num_devices']}")
    report_lines.append("")
    
    # Sauvegarder le rapport
    with open('lorawan_analysis_report.txt', 'w') as f:
        f.write('\n'.join(report_lines))
    
    # Afficher le rapport
    print("\n" + '\n'.join(report_lines))

def main():
    """Fonction principale"""
    print("=== ANALYSE DES RÉSULTATS LORAWAN MAB ===")
    
    # Charger et analyser les données
    df = load_and_analyze()
    
    if df is None or df.empty:
        print("Impossible de charger les résultats")
        return
    
    print("\n" + "=" * 80)
    print(f"ANALYSE TERMINÉE - {len(df)} expériences analysées")
    print("=" * 80)
    
    # Créer les graphiques
    print("\nGénération des graphiques...")
    create_summary_plots(df)
    print("✓ Graphiques sauvegardés:")
    print("  - lorawan_fsr_comparison.png")
    print("  - lorawan_fairness_comparison.png") 
    print("  - lorawan_scaling_analysis.png")
    
    # Générer le rapport
    print("\nGénération du rapport...")
    generate_detailed_report(df)
    print("✓ Rapport sauvegardé: lorawan_analysis_report.txt")
    
    print("\n=== ANALYSE TERMINÉE AVEC SUCCÈS ===")

if __name__ == "__main__":
    main()
