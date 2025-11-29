#!/usr/bin/env python3
"""
Script de vérification des dépendances pour les scripts de visualisation LoRaWAN.
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Vérifie la version de Python"""
    print("=== Vérification de Python ===")
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ requis")
        return False
    else:
        print("✓ Version Python compatible")
        return True

def check_package(package_name, import_name=None):
    """Vérifie si un package Python est installé"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'Version inconnue')
            print(f"✓ {package_name}: {version}")
            return True
        else:
            print(f"❌ {package_name}: Non installé")
            return False
    except Exception as e:
        print(f"❌ {package_name}: Erreur - {e}")
        return False

def check_dependencies():
    """Vérifie toutes les dépendances"""
    print("\n=== Vérification des dépendances ===")
    
    dependencies = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
    ]
    
    all_good = True
    for package, import_name in dependencies:
        if not check_package(package, import_name):
            all_good = False
    
    # Vérifier argparse (inclus dans Python standard)
    try:
        import argparse
        print("✓ argparse: Inclus dans Python standard")
    except ImportError:
        print("❌ argparse: Problème avec Python standard")
        all_good = False
    
    return all_good

def install_dependencies():
    """Propose d'installer les dépendances manquantes"""
    print("\n=== Installation des dépendances ===")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Installation terminée")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False
    except FileNotFoundError:
        print("❌ Fichier requirements.txt non trouvé")
        return False

def check_data_files():
    """Vérifie la présence des fichiers de données"""
    print("\n=== Vérification des fichiers de données ===")
    
    import os
    
    expected_dirs = [
        'lorawan_mixed_results_interf',
        'lorawan_mobile_results_interf',
    ]
    
    expected_files = [
        'lorawan_mixed_results_interf/lorawan-logistics-mab-mixed_ALL.csv',
        'lorawan_mobile_results_interf/lorawan-logistics-mab-mobile_interf.csv',
    ]
    
    dirs_found = 0
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Dossier trouvé: {dir_name}")
            dirs_found += 1
        else:
            print(f"⚠ Dossier manquant: {dir_name}")
    
    files_found = 0
    for file_name in expected_files:
        if os.path.exists(file_name):
            print(f"✓ Fichier trouvé: {file_name}")
            files_found += 1
        else:
            print(f"⚠ Fichier manquant: {file_name}")
    
    if files_found == 0:
        print("⚠ Aucun fichier de données trouvé. Exécutez d'abord la simulation.")
    
    return dirs_found > 0 or files_found > 0

def main():
    """Fonction principale"""
    print("🔍 Vérification de l'environnement pour les scripts LoRaWAN")
    print("=" * 60)
    
    # Vérifier Python
    python_ok = check_python_version()
    
    # Vérifier les dépendances
    deps_ok = check_dependencies()
    
    # Vérifier les fichiers de données
    data_ok = check_data_files()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ")
    print("=" * 60)
    
    if python_ok:
        print("✓ Python: Compatible")
    else:
        print("❌ Python: Incompatible")
    
    if deps_ok:
        print("✓ Dépendances: Toutes installées")
    else:
        print("❌ Dépendances: Manquantes")
        
        # Proposer l'installation
        response = input("\n🤔 Voulez-vous installer les dépendances maintenant? (y/N): ")
        if response.lower() in ['y', 'yes', 'oui']:
            if install_dependencies():
                print("✓ Installation réussie")
                deps_ok = True
            else:
                print("❌ Installation échouée")
    
    if data_ok:
        print("✓ Données: Fichiers trouvés")
    else:
        print("⚠ Données: Aucun fichier trouvé")
    
    print("\n" + "=" * 60)
    
    if python_ok and deps_ok:
        print("🎉 Environnement prêt pour l'analyse!")
        print("\nCommandes disponibles:")
        print("  python plot_lorawan_mixed_interf.py")
        print("  python plot_lorawan_mobile_interf.py")
        print("  ./run_simulation.sh plot")
        return 0
    else:
        print("❌ Environnement non prêt")
        print("\nActions requises:")
        if not python_ok:
            print("  - Installer Python 3.7+")
        if not deps_ok:
            print("  - Installer les dépendances: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
