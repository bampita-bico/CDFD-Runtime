import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUT_DIR = '/home/bampita/Projects/CDFD/CDFD-Part-IV-Release/figures'
DATA_FILE = '/home/bampita/Projects/CDFD/CDFD-Part-IV-Release/outputs/universal_collapse.json'

with open(DATA_FILE, 'r') as f:
    data = json.load(f)

time = data['time']
phi_hub = data['phi_hub']
psi_hub = data['psi_hub']
collapsed = data['collapsed_nodes']

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.patch.set_facecolor('white')

# Panel A: Exponential Drive vs Capacity
ax1 = axes[0]
ax1.plot(time, phi_hub, color='#C0392B', lw=2.5, label='Hub Drive (Phi)')
ax1.set_title('A | Exponential Flux Drive', fontweight='bold', color='#1F3864')
ax1.set_xlabel('Time')
ax1.set_ylabel('Flux Intensity')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel B: Operating Ratio (Psi_s) crossing the Threshold
ax2 = axes[1]
ax2.plot(time, psi_hub, color='#2E75B6', lw=2.5, label='Operating Ratio (Psi_s)')
ax2.axhline(1.5, color='red', ls='--', lw=2, label='Collapse Threshold (Psi_s > 1.5)')
ax2.set_title('B | Mujjabi Capacity Limit', fontweight='bold', color='#1F3864')
ax2.set_xlabel('Time')
ax2.set_ylabel('Psi_s')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Panel C: Network Cascade
ax3 = axes[2]
ax3.plot(time, collapsed, color='#27AE60', lw=3, label='Collapsed Nodes')
ax3.set_title('C | Universal Network Cascade', fontweight='bold', color='#1F3864')
ax3.set_xlabel('Time')
ax3.set_ylabel('Nodes with Locked M_s')
ax3.legend()
ax3.grid(True, alpha=0.3)

fig.suptitle('Numerical Verification: Universal Network Collapse via CDFD Engine', fontsize=14, fontweight='bold', color='#1F3864')
plt.tight_layout()

plt.savefig(os.path.join(OUT_DIR, 'universal_cascade.png'), dpi=300)
print("Graph generated and saved.")
