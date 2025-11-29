#!/usr/bin/env python3
"""
Script de visualisation des résultats d'optimisation LoRaWAN
Analyse les performances des différents algorithmes MAB et scénarios
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from datetime import datetime

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['axes.titlesize'] = 12

def load_experiment_results():
    """Charger tous les fichiers de résultats expérimentaux"""
    results_dir = '/home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42/lorawan_results/'
    
    if not os.path.exists(results_dir):
        print(f"Dossier de résultats non trouvé: {results_dir}")
        return None
    
    # Chercher tous les fichiers CSV dans le dossier de résultats
    result_files = glob.glob(os.path.join(results_dir, "res_*.csv"))
    
    if not result_files:
        print("Aucun fichier de résultats trouvé")
        return None
    
    all_results = []
    
    for file_path in result_files:
        try:
            # Extraire les paramètres du nom de fichier
            filename = os.path.basename(file_path)
            print(f"Traitement de: {filename}")
            
            # Différents formats possibles
            scenario = "unknown"
            mab_mode = "unknown"
            num_devices = 0
            tx_interval = 20
            
            if filename.startswith("joint_"):
                scenario = "JOINT_CH_SF"
                parts = filename.replace('.csv', '').split('_')
                if len(parts) >= 3:
                    mab_mode = "MAB_" + parts[1].upper()
                    if 'dev' in parts[2]:
                        num_devices = int(parts[2].replace('dev', ''))
                    if len(parts) > 3 and 's' in parts[3]:
                        tx_interval = int(parts[3].replace('s', ''))
            
            elif filename.startswith("sf_only_"):
                scenario = "SF_ONLY"
                parts = filename.replace('.csv', '').split('_')
                if len(parts) >= 3:
                    mab_mode = "MAB_" + parts[2].upper()
                    if len(parts) > 3 and 'dev' in parts[3]:
                        num_devices = int(parts[3].replace('dev', ''))
            
            elif filename.startswith("res_"):
                # Format: res_SCENARIO_MABMODE_NUMdev_INTERVALs.csv
                parts = filename.replace('.csv', '').split('_')
                if len(parts) >= 5:
                    if parts[1] == "SF" and parts[2] == "ONLY":
                        scenario = "SF_ONLY"
                        mab_mode = "_".join(parts[3:6])  # MAB_COMBINATORIAL par exemple
                        # Chercher le nombre de devices
                        for part in parts:
                            if 'dev' in part:
                                num_devices = int(part.replace('dev', ''))
                                break
                        # Chercher l'intervalle
                        for part in parts:
                            if 's' in part and part != 'devices':
                                tx_interval = int(part.replace('s', ''))
                                break
                    
                    elif parts[1] == "JOINT":
                        scenario = "JOINT_CH_SF"
                        # Trouver le mode MAB
                        mab_start = -1
                        for i, part in enumerate(parts):
                            if part == "MAB":
                                mab_start = i
                                break
                        if mab_start > 0 and mab_start + 1 < len(parts):
                            mab_mode = "MAB_" + parts[mab_start + 1]
                        
                        # Chercher le nombre de devices et l'intervalle
                        for part in parts:
                            if 'dev' in part:
                                num_devices = int(part.replace('dev', ''))
                            elif 's' in part and part != "devices":
                                tx_interval = int(part.replace('s', ''))
            
            elif filename.startswith("test_"):
                # Format test
                if "SF_ONLY" in filename:
                    scenario = "SF_ONLY"
                elif "JOINT" in filename:
                    scenario = "JOINT_CH_SF"
                
                if "COMBINATORIAL" in filename:
                    mab_mode = "MAB_COMBINATORIAL"
                elif "RANDOM" in filename:
                    mab_mode = "MAB_RANDOM"
                
                # Extraire le nombre de devices
                import re
                match = re.search(r'(\d+)dev', filename)
                if match:
                    num_devices = int(match.group(1))
            
            print(f"  Paramètres: scenario={scenario}, mab_mode={mab_mode}, devices={num_devices}, interval={tx_interval}")
            
            # Charger le fichier CSV
            df = pd.read_csv(file_path)
            
            if not df.empty and scenario != "unknown" and mab_mode != "unknown" and num_devices > 0:
                    # Calculer les métriques de performance
                    total_transmissions = len(df)
                    successful_transmissions = df['ack'].sum()
                    fsr = successful_transmissions / total_transmissions if total_transmissions > 0 else 0
                    
                    # Calculer les métriques par device
                    device_stats = df.groupby('deviceId').agg({
                        'ack': ['count', 'sum'],
                        'sf': 'mean',
                        'channel': 'nunique'
                    }).round(4)
                    
                    device_stats.columns = ['total_tx', 'successful_tx', 'avg_sf', 'channels_used']
                    device_stats['device_fsr'] = device_stats['successful_tx'] / device_stats['total_tx']
                    
                    # Fairness Index (Jain's Fairness Index)
                    device_fsr_values = device_stats['device_fsr'].values
                    fairness_index = (np.sum(device_fsr_values) ** 2) / (len(device_fsr_values) * np.sum(device_fsr_values ** 2)) if len(device_fsr_values) > 0 else 0
                    
                    all_results.append({
                        'scenario': scenario,
                        'mab_mode': mab_mode,
                        'num_devices': num_devices,
                        'tx_interval': tx_interval,
                        'total_transmissions': total_transmissions,
                        'successful_transmissions': successful_transmissions,
                        'fsr': fsr,
                        'fairness_index': fairness_index,
                        'avg_sf': df['sf'].mean(),
                        'sf_diversity': df['sf'].nunique(),
                        'channel_diversity': df['channel'].nunique(),
                        'file_path': file_path
                    })
        
        except Exception as e:
            print(f"Erreur lors du traitement de {file_path}: {e}")
    
    if not all_results:
        print("Aucun résultat valide trouvé")
        return None
    
    return pd.DataFrame(all_results)

def create_performance_comparison_plots(results_df):
    """Créer les graphiques de comparaison de performance"""
    
    # Créer le dossier de sortie
    output_dir = '/home/bonice/Bureau/knowledge/ns-allinone-3.42/ns-3.42/lorawan_analysis_plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # Couleurs pour les algorithmes MAB
    mab_colors = {
        'MAB_COMBINATORIAL': '#FF6B6B',
        'MAB_INDEPENDENT': '#4ECDC4', 
        'MAB_UCB1': '#45B7D1',
        'MAB_TOW': '#96CEB4',
        'MAB_RANDOM': '#FFEAA7'
    }
    
    # 1. FSR par algorithme MAB et nombre de devices
    plt.figure(figsize=(14, 8))
    for scenario in results_df['scenario'].unique():
        plt.subplot(1, 2, 1 if scenario == 'SF_ONLY' else 2)
        
        scenario_data = results_df[results_df['scenario'] == scenario]
        
        for mab_mode in scenario_data['mab_mode'].unique():
            mab_data = scenario_data[scenario_data['mab_mode'] == mab_mode]
            mab_data_sorted = mab_data.sort_values('num_devices')
            
            plt.plot(mab_data_sorted['num_devices'], mab_data_sorted['fsr'], 
                    marker='o', label=mab_mode, color=mab_colors.get(mab_mode, 'gray'),
                    linewidth=2, markersize=6)
        
        plt.xlabel('Nombre de Devices')
        plt.ylabel('Frame Success Rate (FSR)')
        plt.title(f'FSR vs Nombre de Devices - {scenario}')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fsr_comparison_by_scenario.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Fairness Index par algorithme
    plt.figure(figsize=(12, 6))
    for i, scenario in enumerate(results_df['scenario'].unique()):
        plt.subplot(1, 2, i+1)
        
        scenario_data = results_df[results_df['scenario'] == scenario]
        
        # Créer un graphique en barres groupées
        mab_modes = scenario_data['mab_mode'].unique()
        x_pos = np.arange(len(mab_modes))
        
        fairness_means = []
        for mab_mode in mab_modes:
            mab_data = scenario_data[scenario_data['mab_mode'] == mab_mode]
            fairness_means.append(mab_data['fairness_index'].mean())
        
        bars = plt.bar(x_pos, fairness_means, color=[mab_colors.get(mode, 'gray') for mode in mab_modes])
        
        plt.xlabel('Algorithme MAB')
        plt.ylabel('Fairness Index')
        plt.title(f'Fairness Index - {scenario}')
        plt.xticks(x_pos, mab_modes, rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, fairness_means):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fairness_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Distribution des SF utilisés
    plt.figure(figsize=(15, 6))
    
    for i, scenario in enumerate(results_df['scenario'].unique()):
        plt.subplot(1, 2, i+1)
        
        scenario_data = results_df[results_df['scenario'] == scenario]
        
        # Créer un heatmap des SF moyens par algorithme et nombre de devices
        pivot_data = scenario_data.pivot_table(values='avg_sf', index='mab_mode', columns='num_devices', aggfunc='mean')
        
        im = plt.imshow(pivot_data.values, cmap='viridis', aspect='auto')
        plt.colorbar(im, label='SF Moyen')
        
        plt.yticks(range(len(pivot_data.index)), pivot_data.index)
        plt.xticks(range(len(pivot_data.columns)), pivot_data.columns)
        plt.xlabel('Nombre de Devices')
        plt.ylabel('Algorithme MAB')
        plt.title(f'SF Moyen Utilisé - {scenario}')
        
        # Ajouter les valeurs dans les cellules
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                if not np.isnan(pivot_data.iloc[i, j]):
                    plt.text(j, i, f'{pivot_data.iloc[i, j]:.1f}', 
                            ha='center', va='center', color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sf_distribution_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Performance globale - Radar chart
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), subplot_kw=dict(projection='polar'))
    
    for i, scenario in enumerate(results_df['scenario'].unique()):
        ax = axes[i]
        scenario_data = results_df[results_df['scenario'] == scenario]
        
        # Calculer les métriques moyennes par algorithme
        metrics = ['fsr', 'fairness_index', 'sf_diversity', 'channel_diversity']
        metric_labels = ['FSR', 'Fairness', 'SF Diversity', 'Channel Diversity']
        
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Fermer le cercle
        
        for mab_mode in scenario_data['mab_mode'].unique():
            mab_data = scenario_data[scenario_data['mab_mode'] == mab_mode]
            
            values = []
            for metric in metrics:
                if metric in ['sf_diversity', 'channel_diversity']:
                    # Normaliser les valeurs de diversité
                    max_val = scenario_data[metric].max()
                    values.append(mab_data[metric].mean() / max_val if max_val > 0 else 0)
                else:
                    values.append(mab_data[metric].mean())
            
            values += values[:1]  # Fermer le cercle
            
            ax.plot(angles, values, 'o-', linewidth=2, label=mab_mode,
                   color=mab_colors.get(mab_mode, 'gray'))
            ax.fill(angles, values, alpha=0.1, color=mab_colors.get(mab_mode, 'gray'))
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels)
        ax.set_title(f'Performance Globale - {scenario}', y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'performance_radar.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Graphiques sauvegardés dans: {output_dir}")
    return output_dir

def generate_summary_report(results_df, output_dir):
    """Générer un rapport de synthèse"""
    
    report_content = f"""# Rapport d'Analyse des Expériences LoRaWAN MAB

## Résumé Exécutif

Cette analyse compare les performances de {len(results_df['mab_mode'].unique())} algorithmes MAB sur {len(results_df['scenario'].unique())} scénarios différents.

**Date de génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Algorithmes Évalués

"""
    
    for mab_mode in sorted(results_df['mab_mode'].unique()):
        report_content += f"- **{mab_mode}**\n"
    
    report_content += f"""
## Scénarios Testés

"""
    
    for scenario in sorted(results_df['scenario'].unique()):
        scenario_data = results_df[results_df['scenario'] == scenario]
        report_content += f"- **{scenario}**: {len(scenario_data)} expériences\n"
        report_content += f"  - Nombre de devices: {sorted(scenario_data['num_devices'].unique())}\n"
        report_content += f"  - Intervalles de transmission: {sorted(scenario_data['tx_interval'].unique())} s\n\n"
    
    # Tableau de performance
    report_content += """## Tableau de Performance Globale

| Algorithme | FSR Moyen | Fairness Index | SF Diversité | Canal Diversité |
|------------|-----------|----------------|---------------|-----------------|
"""
    
    for mab_mode in sorted(results_df['mab_mode'].unique()):
        mab_data = results_df[results_df['mab_mode'] == mab_mode]
        fsr_mean = mab_data['fsr'].mean()
        fairness_mean = mab_data['fairness_index'].mean()
        sf_div_mean = mab_data['sf_diversity'].mean()
        ch_div_mean = mab_data['channel_diversity'].mean()
        
        report_content += f"| {mab_mode} | {fsr_mean:.4f} | {fairness_mean:.4f} | {sf_div_mean:.2f} | {ch_div_mean:.2f} |\n"
    
    # Meilleures performances par métrique
    report_content += """
## Meilleures Performances

"""
    
    best_fsr = results_df.loc[results_df['fsr'].idxmax()]
    best_fairness = results_df.loc[results_df['fairness_index'].idxmax()]
    
    report_content += f"""- **Meilleur FSR:** {best_fsr['mab_mode']} ({best_fsr['fsr']:.4f}) avec {best_fsr['num_devices']} devices
- **Meilleur Fairness Index:** {best_fairness['mab_mode']} ({best_fairness['fairness_index']:.4f}) avec {best_fairness['num_devices']} devices

## Conclusions

1. **Algorithme le plus performant:** """
    
    # Calculer l'algorithme avec le meilleur score composite
    results_summary = results_df.groupby('mab_mode').agg({
        'fsr': 'mean',
        'fairness_index': 'mean'
    }).round(4)
    
    # Score composite (FSR + Fairness)
    results_summary['composite_score'] = results_summary['fsr'] + results_summary['fairness_index']
    best_overall = results_summary['composite_score'].idxmax()
    
    report_content += f"{best_overall}\n"
    report_content += f"2. **Impact du nombre de devices:** FSR diminue généralement avec l'augmentation du nombre de devices\n"
    report_content += f"3. **Diversité des paramètres:** Les algorithmes adaptatifs montrent une meilleure utilisation de l'espace des paramètres\n"
    
    report_content += f"""
## Graphiques Générés

- `fsr_comparison_by_scenario.png`: Comparaison FSR par scénario
- `fairness_comparison.png`: Indices de fairness par algorithme
- `sf_distribution_heatmap.png`: Distribution des SF utilisés
- `performance_radar.png`: Performance globale en radar chart

## Données Complètes

{len(results_df)} expériences au total analysées.

"""
    
    # Sauvegarder le rapport
    with open(os.path.join(output_dir, 'rapport_analyse.md'), 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Rapport sauvegardé: {os.path.join(output_dir, 'rapport_analyse.md')}")

def main():
    """Fonction principale"""
    print("=== Analyse des Résultats d'Expérimentation LoRaWAN ===")
    
    # Charger les résultats
    results_df = load_experiment_results()
    
    if results_df is None:
        print("Impossible de charger les résultats")
        return
    
    print(f"Chargé {len(results_df)} expériences")
    print(f"Scénarios: {sorted(results_df['scenario'].unique())}")
    print(f"Algorithmes MAB: {sorted(results_df['mab_mode'].unique())}")
    print(f"Nombre de devices: {sorted(results_df['num_devices'].unique())}")
    
    # Créer les graphiques
    output_dir = create_performance_comparison_plots(results_df)
    
    # Générer le rapport
    generate_summary_report(results_df, output_dir)
    
    print("\n=== Analyse Terminée ===")
    print(f"Résultats disponibles dans: {output_dir}")

if __name__ == '__main__':
    main()
