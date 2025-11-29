#!/usr/bin/env python3
"""
Script de validation complète des paramètres LoRaWAN
Vérifie que tous les paramètres SF, puissance, payload et BW sont utilisés
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import glob

class LoRaWANParameterValidator:
    """Classe pour valider l'utilisation des paramètres LoRaWAN"""
    
    def __init__(self):
        self.expected_sf = [7, 8, 9, 10, 11]
        self.expected_tx_power = [2, 8]
        self.expected_payload = [50, 100, 150, 200, 250]
        self.expected_bw = [125000, 250000]
        self.total_combinations = len(self.expected_sf) * len(self.expected_tx_power) * len(self.expected_payload) * len(self.expected_bw)
        
    def find_csv_files(self, base_dir="."):
        """Trouve tous les fichiers CSV de résultats LoRaWAN"""
        patterns = [
            "lorawan_*_results*/lorawan-*.csv",
            "lorawan_*_results_*/lorawan-*.csv",
            "**/lorawan-*.csv"
        ]
        
        csv_files = []
        for pattern in patterns:
            files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
            csv_files.extend(files)
        
        # Supprimer les doublons
        csv_files = list(set(csv_files))
        return csv_files
    
    def load_data(self, csv_file):
        """Charge et valide un fichier CSV"""
        try:
            print(f"📂 Chargement: {csv_file}")
            df = pd.read_csv(csv_file)
            
            # Vérifier les colonnes requises
            required_cols = ['sf', 'txPower', 'payload', 'bw', 'success']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"⚠️  Colonnes manquantes: {missing_cols}")
                return None
            
            print(f"✅ Fichier chargé: {len(df)} lignes")
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return None
    
    def validate_parameters(self, df):
        """Valide que tous les paramètres attendus sont présents"""
        print("\n🔍 VALIDATION DES PARAMÈTRES")
        print("=" * 50)
        
        # Vérifier les Spreading Factors
        unique_sf = sorted(df['sf'].unique())
        print(f"SF trouvés: {unique_sf}")
        print(f"SF attendus: {self.expected_sf}")
        sf_ok = set(unique_sf) == set(self.expected_sf)
        print(f"SF complets: {'✅' if sf_ok else '❌'}")
        
        # Vérifier les puissances de transmission
        unique_tx_power = sorted(df['txPower'].unique())
        print(f"Puissances trouvées: {unique_tx_power}")
        print(f"Puissances attendues: {self.expected_tx_power}")
        tx_power_ok = set(unique_tx_power) == set(self.expected_tx_power)
        print(f"Puissances complètes: {'✅' if tx_power_ok else '❌'}")
        
        # Vérifier les payloads
        unique_payload = sorted(df['payload'].unique())
        print(f"Payloads trouvés: {unique_payload}")
        print(f"Payloads attendus: {self.expected_payload}")
        payload_ok = set(unique_payload) == set(self.expected_payload)
        print(f"Payloads complets: {'✅' if payload_ok else '❌'}")
        
        # Vérifier les bandes passantes
        unique_bw = sorted(df['bw'].unique())
        print(f"BW trouvées: {unique_bw}")
        print(f"BW attendues: {self.expected_bw}")
        bw_ok = set(unique_bw) == set(self.expected_bw)
        print(f"BW complètes: {'✅' if bw_ok else '❌'}")
        
        # Vérifier les combinaisons
        combinations = df.groupby(['sf', 'txPower', 'payload', 'bw']).size()
        unique_combinations = len(combinations)
        print(f"\nCombinaisons trouvées: {unique_combinations}")
        print(f"Combinaisons attendues: {self.total_combinations}")
        combinations_ok = unique_combinations == self.total_combinations
        print(f"Combinaisons complètes: {'✅' if combinations_ok else '❌'}")
        
        # Résumé global
        all_ok = sf_ok and tx_power_ok and payload_ok and bw_ok and combinations_ok
        print(f"\n🎯 VALIDATION GLOBALE: {'✅ SUCCÈS' if all_ok else '❌ ÉCHEC'}")
        
        return {
            'sf_ok': sf_ok,
            'tx_power_ok': tx_power_ok,
            'payload_ok': payload_ok,
            'bw_ok': bw_ok,
            'combinations_ok': combinations_ok,
            'all_ok': all_ok,
            'unique_combinations': unique_combinations
        }
    
    def analyze_parameter_usage(self, df):
        """Analyse l'utilisation de chaque paramètre"""
        print("\n📊 ANALYSE D'UTILISATION DES PARAMÈTRES")
        print("=" * 50)
        
        # Comptage par paramètre
        sf_counts = Counter(df['sf'])
        tx_power_counts = Counter(df['txPower'])
        payload_counts = Counter(df['payload'])
        bw_counts = Counter(df['bw'])
        
        print("Utilisation des SF:")
        for sf in self.expected_sf:
            count = sf_counts.get(sf, 0)
            print(f"  SF{sf}: {count} utilisations")
        
        print("\nUtilisation des puissances:")
        for power in self.expected_tx_power:
            count = tx_power_counts.get(power, 0)
            print(f"  {power} dBm: {count} utilisations")
        
        print("\nUtilisation des payloads:")
        for payload in self.expected_payload:
            count = payload_counts.get(payload, 0)
            print(f"  {payload} octets: {count} utilisations")
        
        print("\nUtilisation des BW:")
        for bw in self.expected_bw:
            count = bw_counts.get(bw, 0)
            bw_khz = bw // 1000
            print(f"  {bw_khz} kHz: {count} utilisations")
    
    def create_validation_plots(self, df, output_dir="validation_plots"):
        """Crée des graphiques de validation"""
        print(f"\n📈 GÉNÉRATION DES GRAPHIQUES DE VALIDATION")
        print("=" * 50)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Configuration des graphiques
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Validation des Paramètres LoRaWAN', fontsize=16, fontweight='bold')
        
        # 1. Distribution des SF
        sf_counts = df['sf'].value_counts().sort_index()
        axes[0,0].bar(sf_counts.index, sf_counts.values, color='skyblue', alpha=0.7)
        axes[0,0].set_title('Distribution des Spreading Factors')
        axes[0,0].set_xlabel('SF')
        axes[0,0].set_ylabel('Nombre d\'utilisations')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Distribution des puissances
        power_counts = df['txPower'].value_counts().sort_index()
        axes[0,1].bar(power_counts.index, power_counts.values, color='lightcoral', alpha=0.7)
        axes[0,1].set_title('Distribution des Puissances de Transmission')
        axes[0,1].set_xlabel('Puissance (dBm)')
        axes[0,1].set_ylabel('Nombre d\'utilisations')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Distribution des payloads
        payload_counts = df['payload'].value_counts().sort_index()
        axes[1,0].bar(payload_counts.index, payload_counts.values, color='lightgreen', alpha=0.7)
        axes[1,0].set_title('Distribution des Payloads')
        axes[1,0].set_xlabel('Payload (octets)')
        axes[1,0].set_ylabel('Nombre d\'utilisations')
        axes[1,0].grid(True, alpha=0.3)
        
        # 4. Distribution des BW
        bw_counts = df['bw'].value_counts().sort_index()
        bw_labels = [f"{bw//1000} kHz" for bw in bw_counts.index]
        axes[1,1].bar(range(len(bw_labels)), bw_counts.values, color='orange', alpha=0.7)
        axes[1,1].set_title('Distribution des Bandes Passantes')
        axes[1,1].set_xlabel('Bande Passante')
        axes[1,1].set_ylabel('Nombre d\'utilisations')
        axes[1,1].set_xticks(range(len(bw_labels)))
        axes[1,1].set_xticklabels(bw_labels)
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_file = os.path.join(output_dir, 'parameter_validation.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"📊 Graphique sauvegardé: {plot_file}")
        plt.close()
        
        # Matrice de corrélation des paramètres
        plt.figure(figsize=(10, 8))
        correlation_data = df[['sf', 'txPower', 'payload', 'bw', 'success']].corr()
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5)
        plt.title('Matrice de Corrélation des Paramètres')
        plt.tight_layout()
        corr_file = os.path.join(output_dir, 'parameter_correlation.png')
        plt.savefig(corr_file, dpi=300, bbox_inches='tight')
        print(f"📊 Corrélation sauvegardée: {corr_file}")
        plt.close()
    
    def generate_report(self, validation_results, df, output_dir="validation_plots"):
        """Génère un rapport de validation"""
        report_file = os.path.join(output_dir, "validation_report.txt")
        
        with open(report_file, 'w') as f:
            f.write("RAPPORT DE VALIDATION DES PARAMÈTRES LORAWAN\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Date de validation: {pd.Timestamp.now()}\n")
            f.write(f"Nombre total de transmissions: {len(df)}\n")
            f.write(f"Nombre de dispositifs: {df['deviceId'].nunique()}\n\n")
            
            f.write("PARAMÈTRES ATTENDUS:\n")
            f.write(f"- SF: {self.expected_sf}\n")
            f.write(f"- Puissances: {self.expected_tx_power} dBm\n")
            f.write(f"- Payloads: {self.expected_payload} octets\n")
            f.write(f"- BW: {[bw//1000 for bw in self.expected_bw]} kHz\n")
            f.write(f"- Combinaisons attendues: {self.total_combinations}\n\n")
            
            f.write("RÉSULTATS DE VALIDATION:\n")
            f.write(f"- SF complets: {'✅' if validation_results['sf_ok'] else '❌'}\n")
            f.write(f"- Puissances complètes: {'✅' if validation_results['tx_power_ok'] else '❌'}\n")
            f.write(f"- Payloads complets: {'✅' if validation_results['payload_ok'] else '❌'}\n")
            f.write(f"- BW complètes: {'✅' if validation_results['bw_ok'] else '❌'}\n")
            f.write(f"- Combinaisons trouvées: {validation_results['unique_combinations']}\n")
            f.write(f"- Toutes combinaisons: {'✅' if validation_results['combinations_ok'] else '❌'}\n\n")
            
            f.write(f"VALIDATION GLOBALE: {'✅ SUCCÈS' if validation_results['all_ok'] else '❌ ÉCHEC'}\n")
        
        print(f"📄 Rapport sauvegardé: {report_file}")

def main():
    """Fonction principale"""
    print("🔍 VALIDATION DES PARAMÈTRES LORAWAN")
    print("=" * 60)
    print("Ce script vérifie que tous les paramètres sont utilisés:")
    print("- SF: 7, 8, 9, 10, 11")
    print("- Puissances: 2, 8 dBm")
    print("- Payloads: 50, 100, 150, 200, 250 octets")
    print("- BW: 125, 250 kHz")
    print("=" * 60)
    
    validator = LoRaWANParameterValidator()
    
    # Trouver les fichiers CSV
    csv_files = validator.find_csv_files()
    
    if not csv_files:
        print("❌ Aucun fichier CSV de résultats trouvé")
        print("💡 Exécutez d'abord une simulation pour générer des données")
        return 1
    
    print(f"📁 {len(csv_files)} fichier(s) CSV trouvé(s):")
    for csv_file in csv_files:
        print(f"   - {csv_file}")
    
    # Analyser chaque fichier
    all_results = []
    combined_df = pd.DataFrame()
    
    for csv_file in csv_files:
        print(f"\n{'='*60}")
        print(f"ANALYSE: {os.path.basename(csv_file)}")
        print(f"{'='*60}")
        
        df = validator.load_data(csv_file)
        if df is not None:
            # Validation
            results = validator.validate_parameters(df)
            all_results.append(results)
            
            # Analyse d'utilisation
            validator.analyze_parameter_usage(df)
            
            # Ajouter au DataFrame combiné
            df['source_file'] = os.path.basename(csv_file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Analyse globale si plusieurs fichiers
    if len(csv_files) > 1:
        print(f"\n{'='*60}")
        print("ANALYSE GLOBALE (TOUS LES FICHIERS)")
        print(f"{'='*60}")
        
        global_results = validator.validate_parameters(combined_df)
        validator.analyze_parameter_usage(combined_df)
        
        # Créer les graphiques
        validator.create_validation_plots(combined_df)
        validator.generate_report(global_results, combined_df)
    
    elif len(csv_files) == 1:
        # Créer les graphiques pour le fichier unique
        validator.create_validation_plots(combined_df)
        validator.generate_report(all_results[0], combined_df)
    
    # Résumé final
    print(f"\n{'='*60}")
    print("RÉSUMÉ FINAL")
    print(f"{'='*60}")
    
    success_count = sum(1 for result in all_results if result['all_ok'])
    print(f"Fichiers validés avec succès: {success_count}/{len(all_results)}")
    
    if success_count == len(all_results):
        print("🎉 TOUS LES PARAMÈTRES SONT CORRECTEMENT UTILISÉS!")
        print("✅ La simulation prend bien en compte:")
        print("   - Tous les SF (7,8,9,10,11)")
        print("   - Toutes les puissances (2,8 dBm)")
        print("   - Tous les payloads (50,100,150,200,250)")
        print("   - Toutes les BW (125,250 kHz)")
        return 0
    else:
        print("⚠️  Certains paramètres ne sont pas correctement utilisés")
        print("📋 Consultez les détails ci-dessus pour plus d'informations")
        return 1

if __name__ == "__main__":
    sys.exit(main())
