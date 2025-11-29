#!/usr/bin/env python3
"""
Script de vérification des paramètres utilisés dans les simulations LoRaWAN
Analyse le fichier CSV généré pour confirmer que tous les paramètres sont pris en compte
"""

import pandas as pd
import sys
import os

def verify_parameters(csv_file):
    """Vérifie que tous les paramètres sont utilisés dans le fichier CSV"""
    print("=" * 60)
    print("🔍 VÉRIFICATION DES PARAMÈTRES LORAWAN")
    print("=" * 60)
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier CSV non trouvé: {csv_file}")
        return False
    
    # Lire le fichier CSV
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Fichier CSV lu avec succès: {len(df)} lignes")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV: {e}")
        return False
    
    # Paramètres attendus
    expected_sf = [7, 8, 9, 10, 11]
    expected_txpower = [2, 8]
    expected_payload = [50, 100, 150, 200, 250]
    expected_bw = [125000, 250000]
    
    # Vérifier les SF
    print("\n📊 ANALYSE DES SPREADING FACTORS:")
    unique_sf = sorted(df['sf'].unique())
    print(f"   Attendu: {expected_sf}")
    print(f"   Trouvé:  {unique_sf}")
    if set(unique_sf) == set(expected_sf):
        print("   ✅ TOUS LES SF SONT UTILISÉS")
    else:
        print("   ❌ SF MANQUANTS")
        missing = set(expected_sf) - set(unique_sf)
        if missing:
            print(f"   Manquants: {missing}")
    
    # Vérifier les puissances
    print("\n⚡ ANALYSE DES PUISSANCES DE TRANSMISSION:")
    unique_txpower = sorted(df['txPower'].unique())
    print(f"   Attendu: {expected_txpower}")
    print(f"   Trouvé:  {unique_txpower}")
    if set(unique_txpower) == set(expected_txpower):
        print("   ✅ TOUTES LES PUISSANCES SONT UTILISÉES")
    else:
        print("   ❌ PUISSANCES MANQUANTES")
        missing = set(expected_txpower) - set(unique_txpower)
        if missing:
            print(f"   Manquantes: {missing}")
    
    # Vérifier les payloads
    print("\n📦 ANALYSE DES PAYLOADS:")
    unique_payload = sorted(df['payload'].unique())
    print(f"   Attendu: {expected_payload}")
    print(f"   Trouvé:  {unique_payload}")
    if set(unique_payload) == set(expected_payload):
        print("   ✅ TOUS LES PAYLOADS SONT UTILISÉS")
    else:
        print("   ❌ PAYLOADS MANQUANTS")
        missing = set(expected_payload) - set(unique_payload)
        if missing:
            print(f"   Manquants: {missing}")
    
    # Vérifier les bandes passantes
    print("\n📡 ANALYSE DES BANDES PASSANTES:")
    unique_bw = sorted(df['bw'].unique())
    print(f"   Attendu: {expected_bw}")
    print(f"   Trouvé:  {unique_bw}")
    if set(unique_bw) == set(expected_bw):
        print("   ✅ TOUTES LES BANDES PASSANTES SONT UTILISÉES")
    else:
        print("   ❌ BANDES PASSANTES MANQUANTES")
        missing = set(expected_bw) - set(unique_bw)
        if missing:
            print(f"   Manquantes: {missing}")
    
    # Calculer le nombre total de combinaisons
    total_combinations = len(expected_sf) * len(expected_txpower) * len(expected_payload) * len(expected_bw)
    print(f"\n🔢 CALCUL DES COMBINAISONS:")
    print(f"   Combinaisons théoriques: {total_combinations}")
    print(f"   ({len(expected_sf)} SF × {len(expected_txpower)} TxPower × {len(expected_payload)} Payload × {len(expected_bw)} BW)")
    
    # Vérifier les combinaisons uniques dans les données
    unique_combinations = df[['sf', 'txPower', 'payload', 'bw']].drop_duplicates()
    print(f"   Combinaisons trouvées: {len(unique_combinations)}")
    
    if len(unique_combinations) == total_combinations:
        print("   ✅ TOUTES LES COMBINAISONS SONT PRÉSENTES")
    else:
        print("   ⚠️  COMBINAISONS PARTIELLES")
        print(f"   Pourcentage: {len(unique_combinations)/total_combinations*100:.1f}%")
    
    # Statistiques par paramètre
    print(f"\n📈 STATISTIQUES D'UTILISATION:")
    for sf in expected_sf:
        count = len(df[df['sf'] == sf])
        print(f"   SF {sf}: {count} transmissions")
    
    for txp in expected_txpower:
        count = len(df[df['txPower'] == txp])
        print(f"   TxPower {txp} dBm: {count} transmissions")
    
    for bw in expected_bw:
        count = len(df[df['bw'] == bw])
        bw_khz = bw // 1000
        print(f"   BW {bw_khz} kHz: {count} transmissions")
    
    # Résumé final
    print("\n" + "=" * 60)
    all_params_ok = (
        set(unique_sf) == set(expected_sf) and
        set(unique_txpower) == set(expected_txpower) and
        set(unique_payload) == set(expected_payload) and
        set(unique_bw) == set(expected_bw)
    )
    
    if all_params_ok:
        print("🎉 RÉSULTAT: TOUS LES PARAMÈTRES SONT CORRECTEMENT UTILISÉS!")
        print("✅ La simulation prend bien en compte:")
        print("   - Tous les Spreading Factors (7,8,9,10,11)")
        print("   - Toutes les puissances de transmission (2,8 dBm)")
        print("   - Tous les payloads (50,100,150,200,250 octets)")
        print("   - Toutes les bandes passantes (125,250 kHz)")
        return True
    else:
        print("❌ RÉSULTAT: CERTAINS PARAMÈTRES NE SONT PAS UTILISÉS")
        return False

def main():
    """Fonction principale"""
    # Fichier CSV par défaut
    csv_file = "lorawan_static_results_interf/lorawan-static-interf_ALL.csv"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    print(f"Analyse du fichier: {csv_file}")
    success = verify_parameters(csv_file)
    
    if success:
        print("\n💡 La simulation est correctement configurée!")
        return 0
    else:
        print("\n⚠️  Vérifiez la configuration de la simulation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
