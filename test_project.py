#!/usr/bin/env python3
"""
Script de test rapide pour vérifier la configuration du projet LoRaWAN.
"""

import os
import sys
import subprocess
import glob

def check_ns3_installation():
    """Vérifie que NS-3 est installé et configuré"""
    print("=== Vérification NS-3 ===")
    
    ns3_dir = "ns-3.42"
    if not os.path.exists(ns3_dir):
        print(f"❌ Dossier {ns3_dir} non trouvé")
        return False
    
    # Vérifier le script ns3
    ns3_script = os.path.join(ns3_dir, "ns3")
    if not os.path.exists(ns3_script):
        print(f"❌ Script ns3 non trouvé dans {ns3_dir}")
        return False
    
    print(f"✓ NS-3 installé dans {ns3_dir}")
    return True

def check_simulation_files():
    """Vérifie la présence des fichiers de simulation LoRaWAN"""
    print("\n=== Vérification des simulations LoRaWAN ===")
    
    scratch_dir = "ns-3.42/scratch"
    if not os.path.exists(scratch_dir):
        print(f"❌ Dossier {scratch_dir} non trouvé")
        return False
    
    expected_files = [
        "lorawan-logistics-mab-static.cc",
        "lorawan-logistics-mab-static-interf.cc",
        "lorawan-logistics-mab-mobile.cc",
        "lorawan-logistics-mab-mobile-interf.cc",
        "lorawan-logistics-mab-mixed.cc",
        "lorawan-logistics-mab-mixed-interf.cc"
    ]
    
    found_files = []
    for pattern in expected_files:
        files = glob.glob(os.path.join(scratch_dir, pattern))
        if files:
            found_files.extend(files)
            print(f"✓ {pattern}")
        else:
            print(f"❌ {pattern} non trouvé")
    
    return len(found_files) == len(expected_files)

def check_automation_scripts():
    """Vérifie la présence des scripts d'automatisation"""
    print("\n=== Vérification des scripts d'automatisation ===")
    
    scripts = [
        "run_simulation.sh",
        "check_environment.py",
        "requirements.txt"
    ]
    
    all_found = True
    for script in scripts:
        if os.path.exists(script):
            print(f"✓ {script}")
        else:
            print(f"❌ {script} non trouvé")
            all_found = False
    
    return all_found

def check_visualization_scripts():
    """Vérifie la présence des scripts de visualisation"""
    print("\n=== Vérification des scripts de visualisation ===")
    
    scripts_dir = "scripts"
    if not os.path.exists(scripts_dir):
        print(f"❌ Dossier {scripts_dir} non trouvé")
        return False
    
    expected_scripts = [
        "plot_lorawan_static.py",
        "plot_lorawan_mobile.py",
        "plot_lorawan_mixed.py",
        "analyze_results.py"
    ]
    
    found_scripts = []
    for script in expected_scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            found_scripts.append(script)
            print(f"✓ {script}")
        else:
            print(f"❌ {script} non trouvé")
    
    return len(found_scripts) == len(expected_scripts)

def main():
    """Fonction principale"""
    print("🔍 Test de configuration du projet LoRaWAN NS-3")
    print("=" * 60)
    
    checks = [
        check_ns3_installation,
        check_simulation_files,
        check_automation_scripts,
        check_visualization_scripts
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 60)
    print("📊 Résumé des vérifications")
    print("=" * 60)
    
    if all(results):
        print("✅ Tous les tests sont passés avec succès !")
        print("🚀 Le projet est prêt à être utilisé.")
        print("\nÉtapes suivantes :")
        print("1. Vérifier l'environnement Python : python3 check_environment.py")
        print("2. Compiler NS-3 : ./run_simulation.sh compile")
        print("3. Exécuter une simulation : ./run_simulation.sh run lorawan-logistics-mab-static")
        return 0
    else:
        print("❌ Certains tests ont échoué.")
        print("📋 Vérifiez les erreurs ci-dessus et consultez le README.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
