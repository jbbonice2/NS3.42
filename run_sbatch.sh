#!/bin/zsh
#SBATCH --job-name=run_time
#SBATCH --output=output.log
#SBATCH --ntasks=1
#SBATCH --partition=p_12G
#SBATCH --gres=gpu:t2080ti:1

cd ns-3.42/scratch || { echo "Le dossier script/ n'existe pas"; exit 1; }

# Exécuter tous les scripts run_s1*.sh en parallèle
for f in run_s1*.sh; do
    chmod +x "$f"
    bash "$f" &
done

wait
echo "Tous les scripts ont terminé."


