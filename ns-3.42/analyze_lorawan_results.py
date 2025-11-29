#!/usr/bin/env python3
"""
Script d'analyse des résultats de comparaison d'algorithmes LoRaWAN
Génère des graphiques et statistiques détaillées à partir des résultats CSV
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os
from pathlib import Path

def load_results(csv_file):
    """Charger les résultats depuis le fichier CSV"""
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} simulation results from {csv_file}")
        return df
    except Exception as e:
        print(f"Error loading {csv_file}: {e}")
        return None

def analyze_algorithm_performance(df):
    """Analyser les performances par algorithme"""
    print("\n=== PERFORMANCE BY ALGORITHM ===")
    
    # Statistiques globales par algorithme
    stats = df.groupby('algorithm').agg({
        'PDR': ['mean', 'std', 'min', 'max'],
        'EC': ['mean', 'std', 'min', 'max']
    }).round(4)
    
    print("\nPDR Statistics (%):")
    print(stats['PDR'])
    
    print("\nEnergy Consumption Statistics (J):")
    print(stats['EC'])
    
    return stats

def analyze_scalability(df):
    """Analyser la scalabilité en fonction du nombre de nœuds"""
    print("\n=== SCALABILITY ANALYSIS ===")
    
    # Filtre les simulations de 1 jour pour l'analyse de scalabilité
    scalability_df = df[df['simTime'] == 86400]
    
    if scalability_df.empty:
        print("No 1-day simulations found for scalability analysis")
        return
    
    print(f"Analyzing {len(scalability_df)} scalability simulations")
    
    # Statistiques par nombre de nœuds
    scale_stats = scalability_df.groupby(['nDevices', 'algorithm']).agg({
        'PDR': 'mean',
        'EC': 'mean'
    }).round(4)
    
    print("\nAverage PDR and Energy by number of devices:")
    print(scale_stats.head(20))

def analyze_learning_duration(df):
    """Analyser l'impact de la durée d'apprentissage"""
    print("\n=== LEARNING DURATION ANALYSIS ===")
    
    # Convertir le temps de simulation en jours
    df['simDays'] = df['simTime'] / 86400
    
    # Filtre pour une taille fixe (100 nœuds)
    learning_df = df[df['nDevices'] == 100]
    
    if learning_df.empty:
        print("No 100-device simulations found for learning analysis")
        return
    
    print(f"Analyzing {len(learning_df)} learning duration simulations")
    
    # Statistiques par durée de simulation
    learning_stats = learning_df.groupby(['simDays', 'algorithm']).agg({
        'PDR': 'mean',
        'EC': 'mean'
    }).round(4)
    
    print("\nAverage PDR and Energy by simulation duration:")
    print(learning_stats.head(20))

def analyze_environment_impact(df):
    """Analyser l'impact de l'environnement (obstacles)"""
    print("\n=== ENVIRONMENT IMPACT ANALYSIS ===")
    
    # Comparer rural vs urbain
    env_comparison = df.groupby(['obstacles', 'algorithm']).agg({
        'PDR': 'mean',
        'EC': 'mean'
    }).round(4)
    
    print("\nPerformance comparison: Rural (False) vs Urban (True):")
    print(env_comparison)

def create_visualizations(df, output_dir):
    """Créer des visualisations des résultats"""
    print(f"\n=== CREATING VISUALIZATIONS in {output_dir} ===")
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(exist_ok=True)
    
    # Style des graphiques
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. Performance globale par algorithme
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # PDR par algorithme
    df.boxplot(column='PDR', by='algorithm', ax=ax1)
    ax1.set_title('Packet Delivery Ratio by Algorithm')
    ax1.set_ylabel('PDR (%)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Énergie par algorithme
    df.boxplot(column='EC', by='algorithm', ax=ax2)
    ax2.set_title('Energy Consumption by Algorithm')
    ax2.set_ylabel('Energy (J)')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/algorithm_performance.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Scalabilité - PDR vs nombre de nœuds
    if 'nDevices' in df.columns:
        plt.figure(figsize=(12, 8))
        for algo in df['algorithm'].unique():
            algo_data = df[df['algorithm'] == algo]
            scale_data = algo_data.groupby('nDevices')['PDR'].mean()
            plt.plot(scale_data.index, scale_data.values, marker='o', label=algo, linewidth=2)
        
        plt.xlabel('Number of Devices')
        plt.ylabel('Average PDR (%)')
        plt.title('Scalability: PDR vs Number of Devices')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/scalability_pdr.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Efficacité énergétique vs PDR
    plt.figure(figsize=(10, 8))
    algorithms = df['algorithm'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))
    
    for i, algo in enumerate(algorithms):
        algo_data = df[df['algorithm'] == algo]
        plt.scatter(algo_data['EC'], algo_data['PDR'], 
                   alpha=0.6, label=algo, s=60, color=colors[i])
    
    plt.xlabel('Energy Consumption (J)')
    plt.ylabel('PDR (%)')
    plt.title('Energy Efficiency vs PDR')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/energy_vs_pdr.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Impact de l'environnement
    if 'obstacles' in df.columns:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # PDR par environnement
        sns.boxplot(data=df, x='algorithm', y='PDR', hue='obstacles', ax=ax1)
        ax1.set_title('PDR by Environment')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(title='Urban Environment', labels=['Rural', 'Urban'])
        
        # Énergie par environnement
        sns.boxplot(data=df, x='algorithm', y='EC', hue='obstacles', ax=ax2)
        ax2.set_title('Energy Consumption by Environment')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title='Urban Environment', labels=['Rural', 'Urban'])
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/environment_impact.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    print("✓ Visualizations saved successfully")

def generate_summary_report(df, output_file):
    """Générer un rapport de synthèse"""
    print(f"\n=== GENERATING SUMMARY REPORT: {output_file} ===")
    
    with open(output_file, 'w') as f:
        f.write("LoRaWAN Algorithm Comparison - Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        # Informations générales
        f.write(f"Total simulations analyzed: {len(df)}\n")
        f.write(f"Algorithms tested: {', '.join(df['algorithm'].unique())}\n")
        if 'nDevices' in df.columns:
            f.write(f"Device range: {df['nDevices'].min()}-{df['nDevices'].max()}\n")
        if 'simTime' in df.columns:
            days_range = df['simTime'] / 86400
            f.write(f"Simulation duration: {days_range.min():.1f}-{days_range.max():.1f} days\n")
        f.write("\n")
        
        # Top performers
        f.write("TOP PERFORMING ALGORITHMS:\n")
        f.write("-" * 30 + "\n")
        
        # Meilleur PDR
        best_pdr = df.groupby('algorithm')['PDR'].mean().sort_values(ascending=False)
        f.write(f"Best PDR: {best_pdr.index[0]} ({best_pdr.iloc[0]:.2f}%)\n")
        
        # Meilleure efficacité énergétique
        best_energy = df.groupby('algorithm')['EC'].mean().sort_values()
        f.write(f"Best Energy Efficiency: {best_energy.index[0]} ({best_energy.iloc[0]:.4f} J)\n")
        
        # Compromis PDR/Énergie
        df_copy = df.copy()
        df_copy['efficiency_score'] = df_copy['PDR'] / df_copy['EC']
        best_compromise = df_copy.groupby('algorithm')['efficiency_score'].mean().sort_values(ascending=False)
        f.write(f"Best Overall Compromise: {best_compromise.index[0]}\n")
        f.write("\n")
        
        # Statistiques détaillées par algorithme
        f.write("DETAILED STATISTICS BY ALGORITHM:\n")
        f.write("-" * 40 + "\n")
        
        for algo in df['algorithm'].unique():
            algo_data = df[df['algorithm'] == algo]
            f.write(f"\n{algo}:\n")
            f.write(f"  Simulations: {len(algo_data)}\n")
            f.write(f"  PDR: {algo_data['PDR'].mean():.2f}% ± {algo_data['PDR'].std():.2f}%\n")
            f.write(f"  Energy: {algo_data['EC'].mean():.4f} ± {algo_data['EC'].std():.4f} J\n")
            f.write(f"  PDR Range: {algo_data['PDR'].min():.2f}% - {algo_data['PDR'].max():.2f}%\n")
            f.write(f"  Energy Range: {algo_data['EC'].min():.4f} - {algo_data['EC'].max():.4f} J\n")
    
    print("✓ Summary report generated successfully")

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_lorawan_results.py <results.csv> [output_dir]")
        print("Example: python3 analyze_lorawan_results.py simulation_results_20231215_120000/results.csv")
        return
    
    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_output"
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found")
        return
    
    # Charger les données
    df = load_results(csv_file)
    if df is None:
        return
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(exist_ok=True)
    
    # Analyses
    analyze_algorithm_performance(df)
    analyze_scalability(df)
    analyze_learning_duration(df)
    analyze_environment_impact(df)
    
    # Visualisations
    create_visualizations(df, output_dir)
    
    # Rapport de synthèse
    report_file = f"{output_dir}/analysis_report.txt"
    generate_summary_report(df, report_file)
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Output directory: {output_dir}")
    print(f"Generated files:")
    print(f"  - algorithm_performance.png")
    print(f"  - scalability_pdr.png")
    print(f"  - energy_vs_pdr.png")
    print(f"  - environment_impact.png")
    print(f"  - analysis_report.txt")
    print(f"\nTo view the analysis:")
    print(f"  cat {report_file}")
    print(f"  xdg-open {output_dir}/")

if __name__ == "__main__":
    main()
