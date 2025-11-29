#!/usr/bin/env python3
"""
Script de vérification complète du projet LoRaWAN NS-3.42

Ce script vérifie que :
1. Tous les fichiers de simulation sont présents
2. Tous les scripts de visualisation sont présents  
3. Tous les fichiers de documentation sont présents
4. Les dépendances Python sont disponibles
5. La structure du projet est correcte

Auteur: Système d'automatisation NS-3
Date: 2025
"""

import os
import sys
import subprocess
import importlib.util

def check_color_support():
    """Vérifie si le terminal supporte les couleurs"""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def colored_print(text, color_code, bold=False):
    """Affiche du texte coloré"""
    if check_color_support():
        style = '\033[1m' if bold else ''
        print(f"{style}\033[{color_code}m{text}\033[0m")
    else:
        print(text)

def success(text):
    colored_print(f"✅ {text}", "92", bold=True)

def error(text):
    colored_print(f"❌ {text}", "91", bold=True)

def warning(text):
    colored_print(f"⚠️ {text}", "93", bold=True)

def info(text):
    colored_print(f"ℹ️ {text}", "94")

def section(text):
    colored_print(f"\n{'='*60}", "96")
    colored_print(f"📋 {text}", "96", bold=True)
    colored_print(f"{'='*60}", "96")

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        success(f"{description}: {filepath}")
        return True
    else:
        error(f"{description} manquant: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Vérifie qu'un dossier existe"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        success(f"{description}: {dirpath}")
        return True
    else:
        error(f"{description} manquant: {dirpath}")
        return False

def check_python_module(module_name):
    """Vérifie qu'un module Python est disponible"""
    try:
        importlib.import_module(module_name)
        success(f"Module Python '{module_name}' disponible")
        return True
    except ImportError:
        error(f"Module Python '{module_name}' manquant")
        return False

def check_simulation_files():
    """Vérifie les fichiers de simulation LoRaWAN"""
    section("FICHIERS DE SIMULATION LORAWAN")
    
    simulation_files = [
        ("ns-3.42/scratch/lorawan-logistics-mab-static.cc", "Simulation statique"),
        ("ns-3.42/scratch/lorawan-logistics-mab-static-interf.cc", "Simulation statique avec interférences"),
        ("ns-3.42/scratch/lorawan-logistics-mab-mobile.cc", "Simulation mobile"),
        ("ns-3.42/scratch/lorawan-logistics-mab-mobile-interf.cc", "Simulation mobile avec interférences"),
        ("ns-3.42/scratch/lorawan-logistics-mab-mixed.cc", "Simulation mixte"),
        ("ns-3.42/scratch/lorawan-logistics-mab-mixed-interf.cc", "Simulation mixte avec interférences"),
    ]
    
    additional_files = [
        ("ns-3.42/scratch/lorawan-tow-mab-rural.cc", "Simulation rurale"),
        ("ns-3.42/scratch/lorawan-tow-mab-urban.cc", "Simulation urbaine"),
        ("ns-3.42/scratch/lorawan-tow-mab-test.cc", "Simulation de test"),
    ]
    
    results = []
    
    info("Vérification des simulations principales (6 fichiers):")
    for filepath, description in simulation_files:
        results.append(check_file_exists(filepath, description))
    
    info("\nVérification des simulations additionnelles:")
    for filepath, description in additional_files:
        results.append(check_file_exists(filepath, description))
    
    return all(results)

def check_visualization_scripts():
    """Vérifie les scripts de visualisation"""
    section("SCRIPTS DE VISUALISATION")
    
    visualization_scripts = [
        ("ns-3.42/scratch/plot_lorawan_static.py", "Script de visualisation statique"),
        ("ns-3.42/scratch/plot_lorawan_mobile.py", "Script de visualisation mobile"),
        ("ns-3.42/scratch/plot_lorawan_mixed.py", "Script de visualisation mixte"),
    ]
    
    legacy_scripts = [
        ("ns-3.42/plot_lorawan_mobile_interf.py", "Script de visualisation mobile (legacy)"),
        ("ns-3.42/plot_all_lorawan.py", "Script de visualisation global"),
    ]
    
    results = []
    
    info("Scripts de visualisation spécialisés:")
    for filepath, description in visualization_scripts:
        results.append(check_file_exists(filepath, description))
    
    info("\nScripts de visualisation globaux:")
    for filepath, description in legacy_scripts:
        results.append(check_file_exists(filepath, description))
    
    return all(results)

def check_documentation_files():
    """Vérifie les fichiers de documentation"""
    section("FICHIERS DE DOCUMENTATION")
    
    documentation_files = [
        ("README.md", "Documentation principale"),
        ("EXECUTION_GUIDE.md", "Guide d'exécution rapide"),
        ("QUICKSTART.md", "Guide de démarrage rapide"),
        ("SYNTHESIS.md", "Synthèse complète du projet"),
        ("ns-3.42/scratch/README_plots.md", "Documentation des graphiques"),
        ("ns-3.42/scratch/README-rural.md", "Documentation simulation rurale"),
        ("ns-3.42/scratch/README-urban.md", "Documentation simulation urbaine"),
    ]
    
    results = []
    
    for filepath, description in documentation_files:
        results.append(check_file_exists(filepath, description))
    
    return all(results)

def check_automation_scripts():
    """Vérifie les scripts d'automatisation"""
    section("SCRIPTS D'AUTOMATISATION")
    
    automation_scripts = [
        ("run_simulation.sh", "Script d'automatisation principal"),
        ("check_environment.py", "Script de vérification d'environnement"),
        ("test_visualization.py", "Script de test des visualisations"),
        ("verify_complete_setup.py", "Script de vérification complète (ce fichier)"),
    ]
    
    results = []
    
    for filepath, description in automation_scripts:
        results.append(check_file_exists(filepath, description))
    
    # Vérifier que les scripts sont exécutables
    executable_scripts = ["run_simulation.sh", "check_environment.py", "test_visualization.py"]
    
    info("\nVérification des permissions d'exécution:")
    for script in executable_scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                success(f"Script exécutable: {script}")
                results.append(True)
            else:
                warning(f"Script non exécutable: {script}")
                results.append(False)
    
    return all(results)

def check_configuration_files():
    """Vérifie les fichiers de configuration"""
    section("FICHIERS DE CONFIGURATION")
    
    config_files = [
        ("requirements.txt", "Dépendances Python"),
        ("config.ini", "Configuration des simulations"),
        (".gitignore", "Fichiers à ignorer Git"),
    ]
    
    results = []
    
    for filepath, description in config_files:
        results.append(check_file_exists(filepath, description))
    
    return all(results)

def check_python_dependencies():
    """Vérifie les dépendances Python"""
    section("DÉPENDANCES PYTHON")
    
    required_modules = [
        "pandas",
        "matplotlib",
        "seaborn", 
        "numpy",
        "argparse",
        "configparser",
        "os",
        "sys",
        "subprocess",
        "glob",
        "datetime",
    ]
    
    results = []
    
    for module in required_modules:
        results.append(check_python_module(module))
    
    return all(results)

def check_ns3_structure():
    """Vérifie la structure NS-3"""
    section("STRUCTURE NS-3")
    
    ns3_dirs = [
        ("ns-3.42", "Dossier principal NS-3"),
        ("ns-3.42/scratch", "Dossier des simulations"),
        ("ns-3.42/src", "Code source NS-3"),
        ("ns-3.42/build", "Dossier de compilation"),
        ("ns-3.42/examples", "Exemples NS-3"),
        ("ns-3.42/src/lorawan", "Module LoRaWAN"),
    ]
    
    results = []
    
    for dirpath, description in ns3_dirs:
        results.append(check_directory_exists(dirpath, description))
    
    # Vérifier le script de build NS-3
    build_script = "ns-3.42/ns3"
    if check_file_exists(build_script, "Script de build NS-3"):
        results.append(True)
    else:
        results.append(False)
    
    return all(results)

def check_result_directories():
    """Vérifie les dossiers de résultats"""
    section("DOSSIERS DE RÉSULTATS")
    
    result_dirs = [
        ("ns-3.42/lorawan_static_results", "Résultats simulation statique"),
        ("ns-3.42/lorawan_static_results_interf", "Résultats simulation statique avec interférences"),
        ("ns-3.42/lorawan_mobile_results", "Résultats simulation mobile"),
        ("ns-3.42/lorawan_mobile_results_interf", "Résultats simulation mobile avec interférences"),
        ("ns-3.42/lorawan_mixed_results", "Résultats simulation mixte"),
        ("ns-3.42/lorawan_mixed_results_interf", "Résultats simulation mixte avec interférences"),
    ]
    
    info("Note: Les dossiers de résultats sont créés automatiquement lors de l'exécution des simulations.")
    
    existing_dirs = 0
    for dirpath, description in result_dirs:
        if check_directory_exists(dirpath, description):
            existing_dirs += 1
        else:
            warning(f"Dossier de résultats sera créé lors de l'exécution: {dirpath}")
    
    info(f"Dossiers de résultats existants: {existing_dirs}/{len(result_dirs)}")
    
    return True  # Toujours vrai car les dossiers sont créés automatiquement

def run_quick_test():
    """Exécute un test rapide des scripts"""
    section("TESTS RAPIDES")
    
    tests = []
    
    # Test du script de vérification d'environnement
    try:
        result = subprocess.run(
            ["python3", "check_environment.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            success("check_environment.py s'exécute correctement")
            tests.append(True)
        else:
            error("check_environment.py a échoué")
            tests.append(False)
    except Exception as e:
        error(f"Erreur lors de l'exécution de check_environment.py: {e}")
        tests.append(False)
    
    # Test du script de test des visualisations
    try:
        result = subprocess.run(
            ["python3", "test_visualization.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            success("test_visualization.py s'exécute correctement")
            tests.append(True)
        else:
            error("test_visualization.py a échoué")
            tests.append(False)
    except Exception as e:
        error(f"Erreur lors de l'exécution de test_visualization.py: {e}")
        tests.append(False)
    
    return all(tests)

def generate_summary_report():
    """Génère un rapport de synthèse"""
    section("RAPPORT DE SYNTHÈSE")
    
    # Compter les fichiers de simulation
    simulation_count = len([f for f in os.listdir("ns-3.42/scratch") if f.endswith('.cc') and 'lorawan' in f])
    
    # Compter les scripts de visualisation
    viz_count = len([f for f in os.listdir("ns-3.42/scratch") if f.startswith('plot_') and f.endswith('.py')])
    
    # Compter les fichiers de documentation
    doc_count = len([f for f in os.listdir(".") if f.endswith('.md')])
    
    info(f"📊 Statistiques du projet:")
    info(f"   • Fichiers de simulation LoRaWAN: {simulation_count}")
    info(f"   • Scripts de visualisation: {viz_count}")
    info(f"   • Fichiers de documentation: {doc_count}")
    
    # Vérifier la taille du README
    readme_size = os.path.getsize("README.md")
    info(f"   • Taille du README: {readme_size} octets")
    
    # Vérifier les dépendances
    try:
        with open("requirements.txt", "r") as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        info(f"   • Dépendances Python: {len(deps)}")
    except Exception as e:
        warning(f"Impossible de lire requirements.txt: {e}")

def main():
    """Fonction principale"""
    colored_print("\n🚀 VÉRIFICATION COMPLÈTE DU PROJET LORAWAN NS-3.42", "95", bold=True)
    colored_print("=" * 70, "95")
    
    # Vérifier que nous sommes dans le bon dossier
    if not os.path.exists("ns-3.42"):
        error("Erreur: Ce script doit être exécuté depuis le dossier ns-allinone-3.42")
        sys.exit(1)
    
    # Exécuter toutes les vérifications
    checks = [
        ("Fichiers de simulation", check_simulation_files),
        ("Scripts de visualisation", check_visualization_scripts),
        ("Documentation", check_documentation_files),
        ("Scripts d'automatisation", check_automation_scripts),
        ("Fichiers de configuration", check_configuration_files),
        ("Dépendances Python", check_python_dependencies),
        ("Structure NS-3", check_ns3_structure),
        ("Dossiers de résultats", check_result_directories),
        ("Tests rapides", run_quick_test),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            error(f"Erreur lors de la vérification {check_name}: {e}")
            results.append((check_name, False))
    
    # Générer le rapport de synthèse
    generate_summary_report()
    
    # Afficher le résumé final
    section("RÉSUMÉ FINAL")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        if result:
            success(f"{check_name}: PASS")
        else:
            error(f"{check_name}: FAIL")
    
    colored_print(f"\n📊 RÉSULTAT GLOBAL:", "96", bold=True)
    if passed == total:
        success(f"Toutes les vérifications ont réussi! ({passed}/{total})")
        colored_print("🎉 Le projet est entièrement configuré et prêt à l'emploi!", "92", bold=True)
    else:
        warning(f"Vérifications réussies: {passed}/{total}")
        colored_print("⚠️ Certaines vérifications ont échoué. Consultez les détails ci-dessus.", "93", bold=True)
    
    # Instructions finales
    section("INSTRUCTIONS FINALES")
    info("Pour exécuter les simulations:")
    info("  ./run_simulation.sh all")
    info("")
    info("Pour exécuter une simulation spécifique:")
    info("  cd ns-3.42")
    info("  ./ns3 run lorawan-logistics-mab-mixed-interf")
    info("")
    info("Pour générer des graphiques:")
    info("  python3 ns-3.42/scratch/plot_lorawan_mixed.py lorawan_mixed_results_interf/")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        error("\nInterrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        error(f"Erreur inattendue: {e}")
        sys.exit(1)
