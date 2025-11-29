#!/usr/bin/env python3
"""
Script simplifié d'analyse des résultats LoRaWAN MAB
Analyse les performances des différents algorithmes et génère des graphiques
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import seaborn as sns
from datetime import datetime

# Configuration des graphiques
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def parse_filename(filename):
    """Parse le nom de fichier pour extraire les paramètres expérimentaux"""
    try:
        # Format: res_SCENARIO_MAB_MODE_Ndev_Ts.csv
        parts = filename.replace('.csv', '').split('_')
        
        if filename.startswith("res_"):
            if len(parts) >= 5:
                if parts[1] == "SF" and parts[2] == "ONLY":
                    scenario = "SF_ONLY"
                    mab_mode = parts[3] + "_" + parts[4]  # MAB_COMBINATORIAL
                    devices = int(parts[5].replace('dev', '')) if len(parts) > 5 and 'dev' in parts[5] else 3
                    interval = int(parts[6].replace('s', '')) if len(parts) > 6 and 's' in parts[6] else 20
                elif parts[1] == "JOINT":
                    scenario = "JOINT_CH_SF"
                    mab_mode = parts[4] + "_" + parts[5]  # MAB_COMBINATORIAL
                    devices = int(parts[6].replace('dev', '')) if len(parts) > 6 and 'dev' in parts[6] else 3
                    interval = int(parts[7].replace('s', '')) if len(parts) > 7 and 's' in parts[7] else 20
                else:
                    scenario = "UNKNOWN"
                    mab_mode = "UNKNOWN"
                    devices = 3
                    interval = 20
            else:
                scenario = "UNKNOWN"
                mab_mode = "UNKNOWN"
                devices = 3
                interval = 20
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

def load_results():
    """Charger tous les fichiers de résultats"""
    results_dir = '/home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42/lorawan_results/'
    
    if not os.path.exists(results_dir):
        print(f"Dossier de résultats non trouvé: {results_dir}")
        return None
    
    result_files = glob.glob(os.path.join(results_dir, "*.csv"))
    
    if not result_files:
        print("Aucun fichier de résultats trouvé")
        return None
    
    all_results = []
    
    for file_path in result_files:
        try:
            filename = os.path.basename(file_path)
            print(f"Traitement de: {filename}")
            
            scenario, mab_mode, num_devices, tx_interval = parse_filename(filename)
            
            if scenario == "UNKNOWN" or mab_mode == "UNKNOWN":
                print(f"  Impossible de parser les paramètres, fichier ignoré")
                continue
            
            print(f"  Paramètres: {scenario}, {mab_mode}, {num_devices} devices, {tx_interval}s")
            
            # Charger le fichier CSV
            df = pd.read_csv(file_path)
            
            if df.empty:
                print(f"  Fichier vide, ignoré")
                continue
            
            # Calculer les métriques
            total_transmissions = len(df)
            successful_transmissions = len(df[df['ack'] == 1])
            fsr = successful_transmissions / total_transmissions if total_transmissions > 0 else 0.0
            
            # Diversité SF
            sf_diversity = len(df['sf'].unique())
            sf_distribution = df['sf'].value_counts().to_dict()
            
            # Diversité canaux
            channel_diversity = len(df['channel'].unique()) if 'channel' in df.columns else 1
            
            # Fairness (Jain's Fairness Index)
            device_success_rates = []
            for device_id in df['deviceId'].unique():
                device_data = df[df['deviceId'] == device_id]
                device_fsr = len(device_data[device_data['ack'] == 1]) / len(device_data) if len(device_data) > 0 else 0.0
                device_success_rates.append(device_fsr)
            
            if len(device_success_rates) > 0:
                fairness_jain = (np.sum(device_success_rates) ** 2) / (len(device_success_rates) * np.sum(np.array(device_success_rates) ** 2))
                fairness_std = 1.0 - np.std(device_success_rates)
            else:
                fairness_jain = 0.0
                fairness_std = 0.0
            
            # Consommation énergétique approximative (basée sur SF)
            energy_factor = df['sf'].apply(lambda x: 2**(x-7)).mean()  # Plus le SF est élevé, plus l'énergie
            
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
                'energy_factor': energy_factor,
                'total_transmissions': total_transmissions,
                'successful_transmissions': successful_transmissions,
                'sf_distribution': sf_distribution
            }
            
            all_results.append(result)
            print(f"  FSR: {fsr:.3f}, Fairness: {fairness_jain:.3f}, SF diversité: {sf_diversity}")
            
        except Exception as e:
            print(f"Erreur lors du traitement de {file_path}: {e}")
            continue
    
    if not all_results:
        print("Aucun résultat valide trouvé")
        return None
    
    return pd.DataFrame(all_results)

def create_performance_comparison_plots(df):
    """Créer des graphiques de comparaison des performances"""
    
    # 1. Comparaison FSR par mode MAB et scénario
    plt.figure(figsize=(14, 10))
    
    # Subplot 1: FSR par mode MAB
    plt.subplot(2, 2, 1)
    fsr_by_mode = df.groupby(['mab_mode', 'scenario'])['fsr'].mean().unstack()
    fsr_by_mode.plot(kind='bar', ax=plt.gca())
    plt.title('Frame Success Rate (FSR) par Mode MAB')
    plt.ylabel('FSR')
    plt.xlabel('Mode MAB')
    plt.xticks(rotation=45)
    plt.legend(title='Scénario')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Fairness par mode MAB
    plt.subplot(2, 2, 2)
    fairness_by_mode = df.groupby(['mab_mode', 'scenario'])['fairness_jain'].mean().unstack()
    fairness_by_mode.plot(kind='bar', ax=plt.gca())
    plt.title('Fairness Index par Mode MAB')
    plt.ylabel('Fairness Index (Jain)')
    plt.xlabel('Mode MAB')
    plt.xticks(rotation=45)
    plt.legend(title='Scénario')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Diversité SF par mode MAB
    plt.subplot(2, 2, 3)
    sf_div_by_mode = df.groupby(['mab_mode', 'scenario'])['sf_diversity'].mean().unstack()
    sf_div_by_mode.plot(kind='bar', ax=plt.gca())
    plt.title('Diversité SF par Mode MAB')
    plt.ylabel('Nombre de SF différents')
    plt.xlabel('Mode MAB')
    plt.xticks(rotation=45)
    plt.legend(title='Scénario')
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Efficacité énergétique (inverse du facteur énergie)
    plt.subplot(2, 2, 4)
    energy_eff = 1.0 / df.groupby(['mab_mode', 'scenario'])['energy_factor'].mean()
    energy_eff.unstack().plot(kind='bar', ax=plt.gca())
    plt.title('Efficacité Énergétique par Mode MAB')
    plt.ylabel('Efficacité Énergétique (1/facteur)')
    plt.xlabel('Mode MAB')
    plt.xticks(rotation=45)
    plt.legend(title='Scénario')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lorawan_mab_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_scaling_analysis(df):
    """Analyser l'impact du nombre de devices"""
    
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: FSR vs nombre de devices
    plt.subplot(2, 3, 1)
    for scenario in df['scenario'].unique():
        for mab_mode in df['mab_mode'].unique():
            subset = df[(df['scenario'] == scenario) & (df['mab_mode'] == mab_mode)]
            if not subset.empty:
                plt.plot(subset['num_devices'], subset['fsr'], 'o-', 
                        label=f'{scenario}-{mab_mode}', alpha=0.7)
    plt.title('FSR vs Nombre de Devices')
    plt.xlabel('Nombre de Devices')
    plt.ylabel('FSR')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Fairness vs nombre de devices
    plt.subplot(2, 3, 2)
    for scenario in df['scenario'].unique():
        for mab_mode in df['mab_mode'].unique():
            subset = df[(df['scenario'] == scenario) & (df['mab_mode'] == mab_mode)]
            if not subset.empty:
                plt.plot(subset['num_devices'], subset['fairness_jain'], 'o-', 
                        label=f'{scenario}-{mab_mode}', alpha=0.7)
    plt.title('Fairness vs Nombre de Devices')
    plt.xlabel('Nombre de Devices')
    plt.ylabel('Fairness Index')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: SF Diversity vs nombre de devices
    plt.subplot(2, 3, 3)
    for scenario in df['scenario'].unique():
        for mab_mode in df['mab_mode'].unique():
            subset = df[(df['scenario'] == scenario) & (df['mab_mode'] == mab_mode)]
            if not subset.empty:
                plt.plot(subset['num_devices'], subset['sf_diversity'], 'o-', 
                        label=f'{scenario}-{mab_mode}', alpha=0.7)
    plt.title('Diversité SF vs Nombre de Devices')
    plt.xlabel('Nombre de Devices')
    plt.ylabel('Nombre de SF différents')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Heatmap des performances par configuration
    plt.subplot(2, 3, 4)
    pivot_fsr = df.pivot_table(values='fsr', index='mab_mode', columns='num_devices', aggfunc='mean')
    sns.heatmap(pivot_fsr, annot=True, fmt='.3f', cmap='RdYlGn')
    plt.title('Heatmap FSR (Mode MAB vs Devices)')
    
    plt.subplot(2, 3, 5)
    pivot_fairness = df.pivot_table(values='fairness_jain', index='mab_mode', columns='num_devices', aggfunc='mean')
    sns.heatmap(pivot_fairness, annot=True, fmt='.3f', cmap='RdYlGn')
    plt.title('Heatmap Fairness (Mode MAB vs Devices)')
    
    plt.subplot(2, 3, 6)
    pivot_sf = df.pivot_table(values='sf_diversity', index='mab_mode', columns='num_devices', aggfunc='mean')
    sns.heatmap(pivot_sf, annot=True, fmt='.1f', cmap='RdYlGn')
    plt.title('Heatmap SF Diversity (Mode MAB vs Devices)')
    
    plt.tight_layout()
    plt.savefig('lorawan_mab_scaling_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_summary_report(df):
    """Générer un rapport de synthèse"""
    
    print("=" * 80)
    print("RAPPORT DE SYNTHÈSE - EXPÉRIMENTATION LORAWAN MAB")
    print("=" * 80)
    
    print(f"\nNombre total d'expériences analysées: {len(df)}")
    print(f"Scénarios testés: {', '.join(df['scenario'].unique())}")
    print(f"Modes MAB testés: {', '.join(df['mab_mode'].unique())}")
    print(f"Tailles de réseau testées: {sorted(df['num_devices'].unique())}")
    
    print("\n" + "=" * 50)
    print("PERFORMANCES MOYENNES PAR MODE MAB")
    print("=" * 50)
    
    summary_stats = df.groupby('mab_mode').agg({
        'fsr': ['mean', 'std'],
        'fairness_jain': ['mean', 'std'],
        'sf_diversity': ['mean', 'std'],
        'energy_factor': ['mean', 'std']
    }).round(4)
    
    print(summary_stats)
    
    print("\n" + "=" * 50)
    print("MEILLEURES CONFIGURATIONS")
    print("=" * 50)
    
    # Meilleure FSR
    best_fsr = df.loc[df['fsr'].idxmax()]
    print(f"Meilleure FSR: {best_fsr['fsr']:.4f}")
    print(f"  Configuration: {best_fsr['mab_mode']} - {best_fsr['scenario']} - {best_fsr['num_devices']} devices")
    
    # Meilleure Fairness
    best_fairness = df.loc[df['fairness_jain'].idxmax()]
    print(f"\nMeilleure Fairness: {best_fairness['fairness_jain']:.4f}")
    print(f"  Configuration: {best_fairness['mab_mode']} - {best_fairness['scenario']} - {best_fairness['num_devices']} devices")
    
    # Meilleure diversité SF
    best_sf_div = df.loc[df['sf_diversity'].idxmax()]
    print(f"\nMeilleure Diversité SF: {best_sf_div['sf_diversity']}")
    print(f"  Configuration: {best_sf_div['mab_mode']} - {best_sf_div['scenario']} - {best_sf_div['num_devices']} devices")
    
    print("\n" + "=" * 50)
    print("COMPARAISON SCÉNARIOS")
    print("=" * 50)
    
    scenario_comparison = df.groupby('scenario').agg({
        'fsr': 'mean',
        'fairness_jain': 'mean',
        'sf_diversity': 'mean'
    }).round(4)
    
    print(scenario_comparison)
    
    # Sauvegarder le rapport
    with open('lorawan_mab_analysis_report.md', 'w') as f:
        f.write("# Rapport d'Analyse LoRaWAN MAB\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Résumé Exécutif\n\n")
        f.write(f"- **Expériences analysées**: {len(df)}\n")
        f.write(f"- **Scénarios**: {', '.join(df['scenario'].unique())}\n")
        f.write(f"- **Modes MAB**: {', '.join(df['mab_mode'].unique())}\n")
        f.write(f"- **Tailles de réseau**: {sorted(df['num_devices'].unique())}\n\n")
        
        f.write("## Performances Moyennes\n\n")
        f.write(f"| Mode MAB | FSR Moyen | Fairness Moyen | Diversité SF |\n")
        f.write(f"|----------|-----------|----------------|-------------|\n")
        
        for mode in df['mab_mode'].unique():
            mode_data = df[df['mab_mode'] == mode]
            fsr_avg = mode_data['fsr'].mean()
            fairness_avg = mode_data['fairness_jain'].mean()
            sf_div_avg = mode_data['sf_diversity'].mean()
            f.write(f"| {mode} | {fsr_avg:.4f} | {fairness_avg:.4f} | {sf_div_avg:.2f} |\n")
        
        f.write(f"\n## Meilleures Configurations\n\n")
        f.write(f"- **Meilleure FSR**: {best_fsr['fsr']:.4f} ({best_fsr['mab_mode']} - {best_fsr['scenario']} - {best_fsr['num_devices']} devices)\n")
        f.write(f"- **Meilleure Fairness**: {best_fairness['fairness_jain']:.4f} ({best_fairness['mab_mode']} - {best_fairness['scenario']} - {best_fairness['num_devices']} devices)\n")
        f.write(f"- **Meilleure Diversité SF**: {best_sf_div['sf_diversity']} ({best_sf_div['mab_mode']} - {best_sf_div['scenario']} - {best_sf_div['num_devices']} devices)\n")
    
    print(f"\nRapport sauvegardé dans: lorawan_mab_analysis_report.md")

def main():
    """Fonction principale"""
    print("=== Analyse des Résultats LoRaWAN MAB ===\n")
    
    # Charger les résultats
    df = load_results()
    
    if df is None or df.empty:
        print("Impossible de charger les résultats")
        return
    
    print(f"\n{len(df)} expériences chargées avec succès\n")
    
    # Créer les graphiques de comparaison
    print("Génération des graphiques de comparaison...")
    create_performance_comparison_plots(df)
    
    print("Génération de l'analyse de scalabilité...")
    create_scaling_analysis(df)
    
    # Générer le rapport de synthèse
    print("Génération du rapport de synthèse...")
    generate_summary_report(df)
    
    print("\n=== Analyse terminée ===")
    print("Graphiques générés:")
    print("- lorawan_mab_performance_comparison.png")
    print("- lorawan_mab_scaling_analysis.png")
    print("Rapport généré:")
    print("- lorawan_mab_analysis_report.md")

if __name__ == "__main__":
    main()
