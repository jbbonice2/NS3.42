reset

# Configuration générale
set terminal pngcairo enhanced font "Helvetica,12"
set output "pdr_vs_time.png"

# Titres et labels
set title "Packet Delivery Ratio (PDR) vs Time"
set xlabel "Time (s)"
set ylabel "PDR (%)"

# Style de la ligne
set style line 1 lc rgb "#0060ad" lt 1 lw 2 pt 7 ps 1.5

# Grille
set grid ytics lc rgb "#bbbbbb" lw 1 lt 0
set grid xtics lc rgb "#bbbbbb" lw 1 lt 0

# Légende
set key top right

# Plot
plot "pdr_vs_time.txt" using 1:2 with linespoints ls 1 title "PDR"

# Configuration pour le deuxième graphique
set output "energy_efficiency_vs_time.png"
set title "Energy Efficiency vs Time"
set ylabel "Energy Efficiency (J/s)"

# Plot
plot "energy_efficiency_vs_time.txt" using 1:2 with linespoints ls 1 title "Energy Efficiency"
