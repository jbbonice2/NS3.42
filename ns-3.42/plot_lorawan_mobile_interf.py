import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

parser = argparse.ArgumentParser(description="Tracer les résultats LoRaWAN à partir d'un dossier de CSV.")
parser.add_argument('csvdir', nargs='?', default=None, help='Dossier contenant les fichiers CSV à utiliser')
args = parser.parse_args()

if args.csvdir:
    csv_dir = args.csvdir
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans le dossier {csv_dir}.")
        exit(1)
else:
    csv_dir = "lorawan_mobile_results_interf"
    csv_files = glob.glob(os.path.join(csv_dir, "lorawan-logistics-mab-mobile_interf.csv"))
    if not csv_files:
        print(f"Aucun fichier CSV trouvé dans le dossier {csv_dir}.")
        exit(1)

for file in csv_files:
    base_name = os.path.splitext(os.path.basename(file))[0]
    PLOTS_DIR = os.path.join(csv_dir, f"{base_name}_plots")
    os.makedirs(PLOTS_DIR, exist_ok=True)
    all_data = []
    df = pd.read_csv(file)
    df['scenario'] = os.path.basename(file)
    # Extraire 'jour' et 'heure' à partir de la colonne 'time'
    if 'time' in df.columns:
        df['jour'] = pd.to_datetime(df['time']).dt.date.astype(str)
        df['heure'] = pd.to_datetime(df['time']).dt.time.astype(str)
    # Calcul dynamique de l'efficacité énergétique (bits/J)
    # energyConsumed est supposé en mWh, conversion en Joules : 1 mWh = 3.6 J
    # Si energyConsumed == 0, on met NaN pour éviter la division par zéro
    df['energyEfficiency'] = (df['payload'] * 8) / (df['energyConsumed'] * 3.6)
    all_data.append(df)
    data = pd.concat(all_data, ignore_index=True)

    def plot_success_rate(df, groupby, fname):
        grouped = df.groupby(groupby).agg({'success': ['mean', 'count']}).reset_index()
        grouped.columns = groupby + ['success_rate', 'count']
        plt.figure(figsize=(10,6))
        sns.barplot(data=grouped, x=groupby[0], y='success_rate', hue=groupby[1] if len(groupby)>1 else None)
        plt.title(f'Taux de succès par {" et ".join(groupby)}')
        plt.ylabel('Taux de succès')
        plt.xlabel(groupby[0])
        plt.ylim(0,1)
        plt.legend(title=groupby[1] if len(groupby)>1 else groupby[0])
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, fname))
        plt.close()

    def plot_metric(df, metric, groupby, fname, ylabel=None):
        grouped = df.groupby(groupby).agg({metric: 'mean'}).reset_index()
        plt.figure(figsize=(12, 7), dpi=150)
        palette = sns.color_palette('Set2', n_colors=grouped[groupby[1]].nunique() if len(groupby)>1 else 8) if len(groupby)>1 else None
        sns.lineplot(
            data=grouped,
            x=groupby[0],
            y=metric,
            hue=groupby[1] if len(groupby)>1 else None,
            marker='o',
            linewidth=2.2,
            markersize=7,
            palette=palette
        )
        plt.title(f'{metric.upper()} moyen par {" et ".join(groupby)}', fontsize=16, fontweight='bold')
        plt.ylabel(ylabel or metric, fontsize=13)
        plt.xlabel(groupby[0], fontsize=13)
        handles, labels = plt.gca().get_legend_handles_labels()
        if len(labels) > 0 and any(l and not l.startswith('_') for l in labels):
            plt.legend(title=groupby[1] if len(groupby)>1 else groupby[0], fontsize=11, title_fontsize=12, loc='best')
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, fname), dpi=300)
        plt.close()

    def plot_metric_vs_message(df, metric, hue, style, fname, ylabel=None):
        plt.figure(figsize=(16, 9), dpi=150)
        if hue and df[hue].nunique() > 1:
            palette = sns.color_palette('tab10', n_colors=df[hue].nunique())
        else:
            palette = None
        ax = sns.lineplot(
            data=df,
            x='messageId',
            y=metric,
            hue=hue if hue and df[hue].nunique() > 1 else None,
            style=style if style and df[style].nunique() > 1 else None,
            errorbar=None,
            marker='o',
            linewidth=2.5,
            markersize=6,
            palette=palette
        )
        plt.title(f'{metric.upper()} selon le numéro de message', fontsize=18, fontweight='bold')
        plt.ylabel(ylabel or metric, fontsize=15)
        plt.xlabel('Numéro de message', fontsize=15)
        handles, labels = ax.get_legend_handles_labels()
        if len(labels) > 0 and any(l and not l.startswith('_') for l in labels):
            plt.legend(title=hue if hue else None, fontsize=12, title_fontsize=13, loc='best')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15, top=0.92)
        plt.savefig(os.path.join(PLOTS_DIR, fname), dpi=300)
        plt.close()

    def plot_metric_vs_time(df, metric, hue, fname, ylabel=None):
        plt.figure(figsize=(16, 9), dpi=150)
        # Si plusieurs jours présents, ajouter 'jour' comme hue secondaire
        jours_uniques = df['jour'].unique() if 'jour' in df.columns else []
        if len(jours_uniques) > 1:
            palette = sns.color_palette('tab10', n_colors=min(len(jours_uniques), 10))
            ax = sns.lineplot(
                data=df,
                x='heure',
                y=metric,
                hue='jour',
                style=hue if hue else None,
                errorbar=None,
                marker='o',
                linewidth=2.5,
                markersize=5,
                palette=palette
            )
            titre_jour = "Plusieurs jours"
        else:
            # Utilise aussi tab10 pour hue si pertinent
            n_cat = df[hue].nunique() if hue and hue in df.columns else 1
            palette = sns.color_palette('tab10', n_colors=min(n_cat, 10)) if n_cat > 1 else None
            ax = sns.lineplot(
                data=df,
                x='heure',
                y=metric,
                hue=hue,
                errorbar=None,
                marker='o',
                linewidth=2.5,
                markersize=5,
                palette=palette
            )
            titre_jour = f"Jour : {jours_uniques[0]}" if len(jours_uniques) == 1 else ""
        titre = f"{metric.upper()} selon l'heure"
        if titre_jour:
            titre += f"\n({titre_jour})"
        plt.title(titre, fontsize=18, fontweight='bold')
        plt.ylabel(ylabel or metric, fontsize=15)
        plt.xlabel('Heure (HH:MM:SS)', fontsize=15)
        # Améliorer la visibilité des ticks d'heure
        ax = plt.gca()
        n_xticks = len(df['heure'].unique())
        max_ticks = 12  # nombre maximal de ticks visibles pour éviter le chevauchement
        if n_xticks > max_ticks:
            xticks_pos = list(range(0, n_xticks, max(1, n_xticks // max_ticks)))
            xticks_labels = df['heure'].unique()[xticks_pos]
            ax.set_xticks(xticks_labels)
            ax.set_xticklabels(xticks_labels, rotation=45, ha='right', fontsize=12)
        else:
            plt.xticks(rotation=45, ha='right', fontsize=12)
        handles, labels = ax.get_legend_handles_labels()
        if len(labels) > 0 and any(l and not l.startswith('_') for l in labels):
            plt.legend(title='jour' if len(jours_uniques) > 1 else (hue if hue else None), fontsize=12, title_fontsize=13, loc='best')
        plt.grid(True, axis='x', linestyle=':', alpha=0.7)  # grille verticale bien visible
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.18, top=0.92)
        plt.savefig(os.path.join(PLOTS_DIR, fname), dpi=300)
        plt.close()

    # Tracés principaux
    plot_success_rate(data, ['sf', 'txPower'], 'success_rate_sf_txPower.png')
    plot_success_rate(data, ['sf', 'payload'], 'success_rate_sf_payload.png')
    plot_success_rate(data, ['sf', 'bw'], 'success_rate_sf_bw.png')

    plot_metric(data, 'rssi', ['sf'], 'rssi_vs_sf.png', ylabel='RSSI (dBm)')
    plot_metric(data, 'snr', ['sf'], 'snr_vs_sf.png', ylabel='SNR (dB)')
    plot_metric(data, 'energyConsumed', ['sf'], 'energy_vs_sf.png', ylabel='Énergie consommée (mWh)')
    plot_metric(data, 'timeOnAir', ['sf'], 'toa_vs_sf.png', ylabel='Temps dans l’air (ms)')

    # Heatmap taux de succès SF x txPower
    if 'txPower' in data.columns:
        pivot = data.pivot_table(index='sf', columns='txPower', values='success', aggfunc='mean')
        plt.figure(figsize=(12,7))
        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='viridis')
        plt.title('Taux de succès (heatmap) SF x txPower')
        plt.ylabel('SF')
        plt.xlabel('txPower (dBm)')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, 'heatmap_success_sf_txPower.png'))
        plt.close()

    # SNR et RSSI en fonction du numéro de message, pour différentes combinaisons
    if 'messageId' in data.columns:
        # SNR : abscisse = messageId, ordonnée = snr, légende = (sf, payload)
        data['sf_payload'] = data['sf'].astype(str) + '-' + data['payload'].astype(str)
        plot_metric_vs_message(data, 'snr', 'sf_payload', None, 'snr_vs_message_sf_payload.png', ylabel='SNR (dB)')
        # RSSI : abscisse = messageId, ordonnée = rssi, légende = (sf, payload)
        plot_metric_vs_message(data, 'rssi', 'sf_payload', None, 'rssi_vs_message_sf_payload.png', ylabel='RSSI (dBm)')
        # SNR : abscisse = messageId, ordonnée = snr, légende = (sf, txPower)
        data['sf_txPower'] = data['sf'].astype(str) + '-' + data['txPower'].astype(str)
        plot_metric_vs_message(data, 'snr', 'sf_txPower', None, 'snr_vs_message_sf_txPower.png', ylabel='SNR (dB)')
        # RSSI : abscisse = messageId, ordonnée = rssi, légende = (sf, txPower)
        plot_metric_vs_message(data, 'rssi', 'sf_txPower', None, 'rssi_vs_message_sf_txPower.png', ylabel='RSSI (dBm)')
        # SNR : abscisse = messageId, ordonnée = snr, légende = (txPower, bw)
        data['txPower_bw'] = data['txPower'].astype(str) + '-' + data['bw'].astype(str)
        plot_metric_vs_message(data, 'snr', 'txPower_bw', None, 'snr_vs_message_txPower_bw.png', ylabel='SNR (dB)')
        # RSSI : abscisse = messageId, ordonnée = rssi, légende = (txPower, bw)
        plot_metric_vs_message(data, 'rssi', 'txPower_bw', None, 'rssi_vs_message_txPower_bw.png', ylabel='RSSI (dBm)')

    # Ajout des courbes demandées : snr, rssi, timeOnAir, energyEfficiency, énergie consommée en fonction du temps
    if 'time' in data.columns:
        # SNR par SF
        plot_metric_vs_time(data, 'snr', 'sf', 'snr_vs_time_sf.png', ylabel='SNR (dB)')
        # SNR par txPower (ch)
        plot_metric_vs_time(data, 'snr', 'txPower', 'snr_vs_time_txPower.png', ylabel='SNR (dB)')
        # SNR global (toutes données confondues, pas de hue)
        def plot_snr_vs_time(df, fname, show_img=True):
            import matplotlib as mpl
            mpl.rcParams['agg.path.chunksize'] = 10000
            import matplotlib.pyplot as plt
            plt.figure(figsize=(16,9), dpi=150)
            df_sorted = df.sort_values('heure')
            plt.plot(df_sorted['heure'], df_sorted['snr'], 'o-', color='blue', alpha=0.7, linewidth=2.5, markersize=4, label='SNR')
            plt.title('SNR en fonction du temps', fontsize=22, fontweight='bold')
            plt.xlabel('Heure (HH:MM:SS)', fontsize=15)
            ax = plt.gca()
            n_xticks = len(df_sorted['heure'].unique())
            max_ticks = 12
            if n_xticks > max_ticks:
                xticks_pos = list(range(0, n_xticks, max(1, n_xticks // max_ticks)))
                xticks_labels = df_sorted['heure'].unique()[xticks_pos]
                ax.set_xticks(xticks_labels)
                ax.set_xticklabels(xticks_labels, rotation=45, ha='right', fontsize=12)
            else:
                plt.xticks(rotation=45, ha='right', fontsize=12)
            plt.ylabel('SNR (dB)', fontsize=18)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(fontsize=15)
            plt.tight_layout()
            plt.savefig(os.path.join(PLOTS_DIR, fname), dpi=300)
            if show_img:
                plt.show()
            plt.close()
        def plot_rssi_vs_time(df, fname, show_img=True):
            import matplotlib as mpl
            mpl.rcParams['agg.path.chunksize'] = 10000
            import matplotlib.pyplot as plt
            plt.figure(figsize=(16,9), dpi=150)
            df_sorted = df.sort_values('heure')
            plt.plot(df_sorted['heure'], df_sorted['rssi'], 'o-', color='green', alpha=0.7, linewidth=2.5, markersize=4, label='RSSI')
            plt.title('RSSI en fonction du temps', fontsize=22, fontweight='bold')
            plt.xlabel('Heure (HH:MM:SS)', fontsize=15)
            ax = plt.gca()
            n_xticks = len(df_sorted['heure'].unique())
            max_ticks = 12
            if n_xticks > max_ticks:
                xticks_pos = list(range(0, n_xticks, max(1, n_xticks // max_ticks)))
                xticks_labels = df_sorted['heure'].unique()[xticks_pos]
                ax.set_xticks(xticks_labels)
                ax.set_xticklabels(xticks_labels, rotation=45, ha='right', fontsize=12)
            else:
                plt.xticks(rotation=45, ha='right', fontsize=12)
            plt.ylabel('RSSI (dBm)', fontsize=18)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(fontsize=15)
            plt.tight_layout()
            plt.savefig(os.path.join(PLOTS_DIR, fname), dpi=300)
            if show_img:
                plt.show()
            plt.close()
        plot_snr_vs_time(data, 'snr_vs_time.png', show_img=True)
        plot_rssi_vs_time(data, 'rssi_vs_time.png', show_img=True)
        # RSSI par SF
        plot_metric_vs_time(data, 'rssi', 'sf', 'rssi_vs_time_sf.png', ylabel='RSSI (dBm)')
        # RSSI par txPower (ch)

        # === Ajout des graphiques globaux demandés ===
        def plot_metric_vs_nDevices_global(df, metric, fname, ylabel=None):
            df = df.copy()
            df['nDevices_binned'] = (df['nDevices'] // 50) * 50
            grouped = df.groupby('nDevices_binned').agg({metric: 'mean'}).reset_index()
            # S'assurer que 0 est inclus même s'il n'y a pas de données pour 0
            if 0 not in grouped['nDevices_binned'].values:
                grouped = pd.concat([pd.DataFrame({'nDevices_binned': [0], metric: [np.nan]}), grouped], ignore_index=True)
            plt.figure(figsize=(10,6))
            plt.plot(grouped['nDevices_binned'], grouped[metric], marker='o')
            plt.title(f'{ylabel or metric} en fonction du nombre de devices')
            plt.xlabel('Nombre de devices')
            plt.ylabel(ylabel or metric)
            plt.grid(True)
            # Forcer les ticks tous les 50
            max_devices = grouped['nDevices_binned'].max()
            plt.xticks(np.arange(0, max_devices + 51, 50))
            plt.tight_layout()
            plt.savefig(os.path.join(PLOTS_DIR, fname))
            plt.close()

        def plot_pdr_vs_nDevices_global(df, fname):
            df = df.copy()
            df['nDevices_binned'] = (df['nDevices'] // 50) * 50
            grouped = df.groupby('nDevices_binned').agg({'success': 'mean'}).reset_index()
            if 0 not in grouped['nDevices_binned'].values:
                grouped = pd.concat([pd.DataFrame({'nDevices_binned': [0], 'success': [np.nan]}), grouped], ignore_index=True)
            plt.figure(figsize=(10,6))
            plt.plot(grouped['nDevices_binned'], grouped['success'], marker='o')
            plt.title('PDR (Packet Delivery Ratio) en fonction du nombre de devices')
            plt.xlabel('Nombre de devices')
            plt.ylabel('PDR (taux de succès)')
            plt.ylim(0, 1)
            plt.grid(True)
            max_devices = grouped['nDevices_binned'].max()
            plt.xticks(np.arange(0, max_devices + 51, 50))
            plt.tight_layout()
            plt.savefig(os.path.join(PLOTS_DIR, fname))
            plt.close()

        plot_metric_vs_nDevices_global(data, 'timeOnAir', 'toa_vs_nDevices.png', ylabel='Time on Air moyen (s)')
        plot_metric_vs_nDevices_global(data, 'snr', 'snr_vs_nDevices.png', ylabel='SNR moyen (dB)')
        plot_metric_vs_nDevices_global(data, 'rssi', 'rssi_vs_nDevices.png', ylabel='RSSI moyen (dBm)')
        plot_metric_vs_nDevices_global(data, 'energyConsumed', 'energy_vs_nDevices.png', ylabel='Énergie consommée moyenne (mWh)')
        plot_metric_vs_nDevices_global(data, 'energyEfficiency', 'efficacite_vs_nDevices.png', ylabel='Efficacité énergétique moyenne (bits/J)')
        plot_pdr_vs_nDevices_global(data, 'pdr_vs_nDevices.png')

        plot_metric_vs_time(data, 'rssi', 'txPower', 'rssi_vs_time_txPower.png', ylabel='RSSI (dBm)')
        # TimeOnAir par SF
        if 'timeOnAir' in data.columns:
            plot_metric_vs_time(data, 'timeOnAir', 'sf', 'toa_vs_time_sf.png', ylabel='Temps dans l’air (ms)')
            plot_metric_vs_time(data, 'timeOnAir', 'txPower', 'toa_vs_time_txPower.png', ylabel='Temps dans l’air (ms)')
        # Efficacité énergétique par SF
        if 'energyEfficiency' in data.columns:
            plot_metric_vs_time(data, 'energyEfficiency', 'sf', 'efficacite_vs_time_sf.png', ylabel='Efficacité énergétique (bits/J)')
            plot_metric_vs_time(data, 'energyEfficiency', 'txPower', 'efficacite_vs_time_txPower.png', ylabel='Efficacité énergétique (bits/J)')
        # Energie consommée par SF
        plot_metric_vs_time(data, 'energyConsumed', 'sf', 'energie_vs_time_sf.png', ylabel='Énergie consommée (mWh)')
        plot_metric_vs_time(data, 'energyConsumed', 'txPower', 'energie_vs_time_txPower.png', ylabel='Énergie consommée (mWh)')

    # PDR (Packet Delivery Ratio) en fonction du nombre de devices
    if 'messageId' in data.columns and 'success' in data.columns and 'sf' in data.columns:
        pdr_grouped = data.groupby(['nDevices', 'sf'])['success'].agg(['sum', 'count']).reset_index()
        pdr_grouped['PDR'] = pdr_grouped['sum'] / pdr_grouped['count']
        plt.figure(figsize=(12,7))
        sns.lineplot(
            data=pdr_grouped,
            x='nDevices',
            y='PDR',
            hue='sf',
            marker='o',
            errorbar=None
        )
        plt.title('PDR en fonction du nombre de devices (SF)')
        plt.ylabel('PDR')
        plt.xlabel('Nombre de devices')
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15, top=0.92)
        plt.savefig(os.path.join(PLOTS_DIR, 'pdr_vs_nDevices_sf.png'))
        plt.close()
    else:
        print("Colonnes 'messageId', 'success' ou 'sf' manquantes pour le calcul du PDR.")

    # Efficacité énergétique en fonction du nombre de devices
    if 'energyEfficiency' in data.columns and 'sf' in data.columns:
        eff_grouped = data.groupby(['nDevices', 'sf'])['energyEfficiency'].mean().reset_index()
        plt.figure(figsize=(12,7))
        sns.lineplot(
            data=eff_grouped,
            x='nDevices',
            y='energyEfficiency',
            hue='sf',
            marker='o',
            errorbar=None
        )
        plt.title('Efficacité énergétique en fonction du nombre de devices (SF)')
        plt.ylabel('Efficacité énergétique (bits/J)')
        plt.xlabel('Nombre de devices')
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15, top=0.92)
        plt.savefig(os.path.join(PLOTS_DIR, 'efficacite_vs_nDevices_sf.png'))
        plt.close()
    else:
        print("Colonne 'energyEfficiency' ou 'sf' manquante pour le calcul de l'efficacité énergétique.")

print(f"Graphiques générés dans les sous-dossiers *_plots/ du dossier {csv_dir}/")
