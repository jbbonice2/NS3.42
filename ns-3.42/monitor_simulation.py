#!/usr/bin/env python3
"""
Script de monitoring pour suivre le progrès des simulations LoRaWAN
"""

import time
import os
import pandas as pd
from datetime import datetime
import sys

def monitor_simulation_progress():
    """Surveille le progrès de la simulation"""
    print("LoRaWAN Simulation Monitor")
    print("=" * 40)
    
    results_file = "results.csv"
    
    if not os.path.exists(results_file):
        print("⚠️  Results file not found yet. Waiting for simulation to start...")
    
    last_count = 0
    start_time = time.time()
    
    while True:
        try:
            if os.path.exists(results_file):
                # Lire le nombre de lignes (sans compter l'en-tête)
                with open(results_file, 'r') as f:
                    lines = f.readlines()
                    current_count = len(lines) - 1  # -1 pour l'en-tête
                
                if current_count > last_count:
                    elapsed = time.time() - start_time
                    progress = (current_count / 408) * 100  # 408 simulations au total
                    
                    # Estimer le temps restant
                    if current_count > 0:
                        time_per_sim = elapsed / current_count
                        remaining_sims = 408 - current_count
                        eta_seconds = remaining_sims * time_per_sim
                        eta_hours = eta_seconds / 3600
                    else:
                        eta_hours = 0
                    
                    print(f"\r🔄 Progress: {current_count}/408 ({progress:.1f}%) | "
                          f"Elapsed: {elapsed/3600:.1f}h | ETA: {eta_hours:.1f}h", end="")
                    
                    last_count = current_count
                    
                    # Afficher les derniers résultats si disponibles
                    if current_count >= 5:
                        try:
                            df = pd.read_csv(results_file)
                            latest = df.tail(1).iloc[0]
                            print(f"\n📊 Latest: {latest['algorithm']} | "
                                  f"PDR: {latest['PDR']:.1f}% | "
                                  f"Energy: {latest['EC']:.3f}J")
                        except:
                            pass
                
                if current_count >= 408:
                    print("\n🎉 Simulation completed!")
                    break
            
            time.sleep(30)  # Vérifier toutes les 30 secondes
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

def show_current_status():
    """Affiche le statut actuel"""
    results_file = "results.csv"
    
    if not os.path.exists(results_file):
        print("❌ No results file found. Simulation may not have started yet.")
        return
    
    try:
        df = pd.read_csv(results_file)
        total_sims = len(df)
        
        print(f"📈 Current Status:")
        print(f"   Total simulations completed: {total_sims}/408")
        print(f"   Progress: {(total_sims/408)*100:.1f}%")
        
        if total_sims > 0:
            print(f"\n🔍 Recent Results:")
            recent = df.tail(5)
            for _, row in recent.iterrows():
                print(f"   {row['algorithm']:12} | {row['nDevices']:4}d | "
                      f"PDR: {row['PDR']:5.1f}% | Energy: {row['EC']:.3f}J")
            
            print(f"\n📊 Algorithm Progress:")
            algo_counts = df['algorithm'].value_counts()
            expected_per_algo = 408 // 6  # 6 algorithmes
            for algo, count in algo_counts.items():
                progress = (count / expected_per_algo) * 100
                print(f"   {algo:12}: {count:3}/{expected_per_algo} ({progress:.1f}%)")
    
    except Exception as e:
        print(f"❌ Error reading results: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_current_status()
    else:
        monitor_simulation_progress()

if __name__ == "__main__":
    main()
