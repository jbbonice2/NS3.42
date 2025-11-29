import matplotlib.pyplot as plt
import numpy as np

# Créer une figure
fig, ax = plt.subplots(figsize=(10, 6))

# Positions des nœuds
gateway_pos = (1000, 0)
end_device_pos = (0, 0)

# Dessiner les nœuds
ax.plot(gateway_pos[0], gateway_pos[1], 'ro', markersize=10, label='Gateway')
ax.plot(end_device_pos[0], end_device_pos[1], 'bo', markersize=10, label='End Device')

# Ajouter des étiquettes
ax.text(gateway_pos[0] + 50, gateway_pos[1], 'Gateway', fontsize=12)
ax.text(end_device_pos[0] + 50, end_device_pos[1], 'End Device', fontsize=12)

# Ajouter une flèche pour représenter la transmission
arrow = plt.arrow(end_device_pos[0], end_device_pos[1], 
                 gateway_pos[0] - end_device_pos[0], 
                 gateway_pos[1] - end_device_pos[1],
                 head_width=50, head_length=100, fc='g', ec='g')

# Configurer l'axe
ax.set_xlim(-200, 1200)
ax.set_ylim(-200, 200)
ax.set_xlabel('Position X (m)')
ax.set_ylabel('Position Y (m)')
ax.set_title('Réseau LoRaWAN Simple')
ax.legend()

# Afficher la figure
plt.grid(True)
plt.show()
