#!/usr/bin/env python3
"""
Script de visualisation des paramètres OLS estimés vs réels dans le temps
pour la simulation LoRaWAN avec l'algorithme NoReL.

Utilisation:
    python3 plot_ols_parameters.py [--file ols_parameter_trace.csv] [--output ols_parameters.png]
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
from pathlib import Path

def load_ols_data(filename):
    """Charge les données de trace OLS depuis le fichier CSV."""
    try:
        df = pd.read_csv(filename)
        print(f"Données chargées: {len(df)} points temporels")
        print(f"Colonnes: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Erreur: Fichier {filename} non trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        return None

def calculate_convergence_metrics(estimated, real):
    """Calcule les métriques de convergence entre valeurs estimées et réelles."""
    # Erreur quadratique moyenne (RMSE)
    rmse = np.sqrt(np.mean((estimated - real) ** 2))
    
    # Erreur absolue moyenne (MAE)
    mae = np.mean(np.abs(estimated - real))
    
    # Erreur relative moyenne en pourcentage
    mape = np.mean(np.abs((estimated - real) / real)) * 100
    
    # Coefficient de corrélation
    correlation = np.corrcoef(estimated, real)[0, 1]
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape,
        'Correlation': correlation
    }

def calculate_confidence_intervals(estimated, real, confidence=0.95):
    """Calcule les intervalles de confiance pour l'estimation."""
    errors = estimated - real
    std_error = np.std(errors)
    
    # Facteur pour intervalle de confiance (approximation normale)
    if confidence == 0.95:
        z_factor = 1.96
    elif confidence == 0.99:
        z_factor = 2.576
    else:
        z_factor = 1.96
    
    margin = z_factor * std_error
    lower_bound = estimated - margin
    upper_bound = estimated + margin
    
    return lower_bound, upper_bound

def plot_ols_parameters(df, output_file="ols_parameters.png"):
    """Génère les graphiques d'évolution des paramètres OLS."""
    
    # Configuration du style
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Évolution des Paramètres de Path Loss: Estimés vs Réels\n(Estimation OLS avec NoReL)', 
                 fontsize=16, fontweight='bold')
    
    time = df['time'].values
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    parameters = [
        ('PL(d₀)', 'real_PL0', 'estimated_PL0', 'dB'),
        ('γ (Exposant)', 'real_gamma', 'estimated_gamma', ''),
        ('σ (Shadowing)', 'real_sigma', 'estimated_sigma', 'dB')
    ]
    
    for i, (param_name, real_col, est_col, unit) in enumerate(parameters):
        ax = axes[i]
        
        real_values = df[real_col].values
        est_values = df[est_col].values
        
        # Calcul des intervalles de confiance
        lower_ci, upper_ci = calculate_confidence_intervals(est_values, real_values)
        
        # Graphique principal
        ax.plot(time, real_values, 'r-', linewidth=2, label=f'{param_name} réel', alpha=0.8)
        ax.plot(time, est_values, 'b--', linewidth=2, label=f'{param_name} estimé (OLS)', alpha=0.8)
        
        # Zone de confiance à 95%
        ax.fill_between(time, lower_ci, upper_ci, alpha=0.2, color='blue', 
                       label='Intervalle confiance 95%')
        
        # Métriques de convergence
        metrics = calculate_convergence_metrics(est_values, real_values)
        
        # Formatage de l'axe
        ax.set_ylabel(f'{param_name} ({unit})' if unit else param_name, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        
        # Annotation des métriques
        textstr = f'RMSE: {metrics["RMSE"]:.3f}\nMAE: {metrics["MAE"]:.3f}\nMAPE: {metrics["MAPE"]:.1f}%\nCorr: {metrics["Correlation"]:.3f}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=8,
                verticalalignment='top', bbox=props)
        
        # Ajuster les limites pour une meilleure visualisation
        y_margin = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.1
        ax.set_ylim(ax.get_ylim()[0] - y_margin, ax.get_ylim()[1] + y_margin)
    
    # Axe X commun
    axes[-1].set_xlabel('Temps (secondes)', fontsize=12)
    
    # Information sur les mesures
    num_measurements = df['num_measurements'].iloc[-1] if len(df) > 0 else 0
    fig.text(0.02, 0.02, f'Nombre total de mesures OLS: {num_measurements}', 
             fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.1)
    
    # Sauvegarde
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graphique sauvegardé: {output_file}")
    
    return fig

def plot_convergence_analysis(df, output_file="ols_convergence.png"):
    """Analyse de la convergence des paramètres OLS."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Analyse de Convergence des Paramètres OLS', fontsize=16, fontweight='bold')
    
    time = df['time'].values
    parameters = [
        ('PL(d₀)', 'real_PL0', 'estimated_PL0'),
        ('γ', 'real_gamma', 'estimated_gamma'),
        ('σ', 'real_sigma', 'estimated_sigma')
    ]
    
    # Graphique 1: Erreurs absolues dans le temps
    ax1 = axes[0, 0]
    for param_name, real_col, est_col in parameters:
        errors = np.abs(df[est_col] - df[real_col])
        ax1.plot(time, errors, label=f'|Erreur {param_name}|', alpha=0.7)
    ax1.set_ylabel('Erreur Absolue')
    ax1.set_xlabel('Temps (s)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Évolution des Erreurs Absolues')
    
    # Graphique 2: RMSE mobile
    ax2 = axes[0, 1]
    window_size = max(10, len(df) // 20)  # Fenêtre adaptative
    for param_name, real_col, est_col in parameters:
        rmse_rolling = []
        for i in range(window_size, len(df)):
            window_data = df.iloc[i-window_size:i]
            rmse = np.sqrt(np.mean((window_data[est_col] - window_data[real_col]) ** 2))
            rmse_rolling.append(rmse)
        
        if rmse_rolling:
            ax2.plot(time[window_size:], rmse_rolling, label=f'RMSE {param_name}', alpha=0.7)
    
    ax2.set_ylabel('RMSE Mobile')
    ax2.set_xlabel('Temps (s)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_title(f'RMSE Mobile (fenêtre: {window_size} points)')
    
    # Graphique 3: Nombre de mesures vs précision
    ax3 = axes[1, 0]
    num_measurements = df['num_measurements'].values
    # Calculer RMSE pour PL(d0) comme métrique de précision
    rmse_pl0 = np.sqrt((df['estimated_PL0'] - df['real_PL0']) ** 2)
    ax3.scatter(num_measurements, rmse_pl0, alpha=0.6, s=20)
    ax3.set_xlabel('Nombre de Mesures OLS')
    ax3.set_ylabel('RMSE PL(d₀)')
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Précision vs Nombre de Mesures')
    
    # Ajout d'une ligne de tendance
    if len(num_measurements) > 1:
        z = np.polyfit(num_measurements, rmse_pl0, 1)
        p = np.poly1d(z)
        ax3.plot(num_measurements, p(num_measurements), "r--", alpha=0.8, linewidth=1)
    
    # Graphique 4: Distribution des erreurs finales
    ax4 = axes[1, 1]
    final_errors = []
    param_names = []
    for param_name, real_col, est_col in parameters:
        if len(df) > 0:
            final_error = df[est_col].iloc[-1] - df[real_col].iloc[-1]
            final_errors.append(final_error)
            param_names.append(param_name)
    
    if final_errors:
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        bars = ax4.bar(param_names, final_errors, color=colors, alpha=0.7)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.set_ylabel('Erreur Finale (Estimé - Réel)')
        ax4.set_title('Erreurs Finales par Paramètre')
        ax4.grid(True, alpha=0.3)
        
        # Annotation des valeurs
        for bar, error in zip(bars, final_errors):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.01),
                    f'{error:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    # Sauvegarde
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Analyse de convergence sauvegardée: {output_file}")
    
    return fig

def print_summary_statistics(df):
    """Affiche les statistiques de résumé."""
    print("\n" + "="*60)
    print("RÉSUMÉ DES STATISTIQUES OLS")
    print("="*60)
    
    parameters = [
        ('PL(d₀)', 'real_PL0', 'estimated_PL0', 'dB'),
        ('γ (Exposant)', 'real_gamma', 'estimated_gamma', ''),
        ('σ (Shadowing)', 'real_sigma', 'estimated_sigma', 'dB')
    ]
    
    for param_name, real_col, est_col, unit in parameters:
        if len(df) > 0:
            real_values = df[real_col].values
            est_values = df[est_col].values
            
            metrics = calculate_convergence_metrics(est_values, real_values)
            
            print(f"\n{param_name}:")
            print(f"  Valeur réelle moyenne: {np.mean(real_values):.3f} {unit}")
            print(f"  Valeur estimée moyenne: {np.mean(est_values):.3f} {unit}")
            print(f"  RMSE: {metrics['RMSE']:.3f} {unit}")
            print(f"  MAE: {metrics['MAE']:.3f} {unit}")
            print(f"  MAPE: {metrics['MAPE']:.1f}%")
            print(f"  Corrélation: {metrics['Correlation']:.3f}")
    
    if len(df) > 0:
        print(f"\nNombre total de points temporels: {len(df)}")
        print(f"Durée de simulation: {df['time'].iloc[-1] - df['time'].iloc[0]:.1f} secondes")
        print(f"Nombre final de mesures OLS: {df['num_measurements'].iloc[-1]}")

def main():
    parser = argparse.ArgumentParser(description='Visualisation des paramètres OLS LoRaWAN')
    parser.add_argument('--file', default='ols_parameter_trace.csv',
                       help='Fichier CSV des traces OLS (défaut: ols_parameter_trace.csv)')
    parser.add_argument('--output', default='ols_parameters.png',
                       help='Fichier de sortie pour le graphique principal (défaut: ols_parameters.png)')
    parser.add_argument('--convergence', default='ols_convergence.png',
                       help='Fichier de sortie pour l\'analyse de convergence (défaut: ols_convergence.png)')
    parser.add_argument('--show', action='store_true',
                       help='Afficher les graphiques à l\'écran')
    
    args = parser.parse_args()
    
    # Vérifier que le fichier existe
    if not Path(args.file).exists():
        print(f"Erreur: Le fichier {args.file} n'existe pas.")
        print("Assurez-vous d'avoir exécuté la simulation LoRaWAN d'abord.")
        sys.exit(1)
    
    # Charger les données
    df = load_ols_data(args.file)
    if df is None or len(df) == 0:
        print("Erreur: Impossible de charger les données ou fichier vide.")
        sys.exit(1)
    
    # Vérifier les colonnes requises
    required_cols = ['time', 'real_PL0', 'estimated_PL0', 'real_gamma', 'estimated_gamma', 
                     'real_sigma', 'estimated_sigma', 'num_measurements']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Erreur: Colonnes manquantes dans le fichier CSV: {missing_cols}")
        sys.exit(1)
    
    # Générer les graphiques
    print("Génération des graphiques...")
    
    # Graphique principal
    fig1 = plot_ols_parameters(df, args.output)
    
    # Analyse de convergence
    fig2 = plot_convergence_analysis(df, args.convergence)
    
    # Statistiques de résumé
    print_summary_statistics(df)
    
    print(f"\nGraphiques générés avec succès:")
    print(f"  - Évolution des paramètres: {args.output}")
    print(f"  - Analyse de convergence: {args.convergence}")
    
    # Afficher les graphiques si demandé
    if args.show:
        plt.show()

if __name__ == "__main__":
    main()
