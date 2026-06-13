import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('output', exist_ok=True)

fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
ax.axis('off')

boxes = {
    '1. Business Understanding\n(Pemetaan Kebijakan JALA)': (0.05, 0.7, 0.25, 0.15),
    '2. Data Understanding\n(Data Udang BPS 23-24)': (0.38, 0.7, 0.25, 0.15),
    '3. Data Preparation\n(Cleaning & RobustScaler)': (0.71, 0.7, 0.25, 0.15),
    '4. Modeling\n(MDS & Spectral K=4)': (0.71, 0.4, 0.25, 0.15),
    '5. Evaluation\n(Silhouette & Stress Score)': (0.38, 0.4, 0.25, 0.15),
    '6. Deployment\n(Implementasi JALA Tech)': (0.05, 0.4, 0.25, 0.15),
}

for name, (x, y, w, h) in boxes.items():
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", 
                                  edgecolor='#2980B9', facecolor='#EAF2F8', lw=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=11, fontweight='bold', color='#2C3E50')

# Draw arrows
kw = dict(arrowprops=dict(arrowstyle="-|>", lw=2, color='#7F8C8D', shrinkA=0, shrinkB=0))

# 1 -> 2
ax.annotate("", xy=(0.38, 0.775), xytext=(0.3, 0.775), **kw)
# 2 -> 3
ax.annotate("", xy=(0.71, 0.775), xytext=(0.63, 0.775), **kw)
# 3 -> 4
ax.annotate("", xy=(0.835, 0.55), xytext=(0.835, 0.7), **kw)
# 4 -> 5
ax.annotate("", xy=(0.63, 0.475), xytext=(0.71, 0.475), **kw)
# 5 -> 6
ax.annotate("", xy=(0.3, 0.475), xytext=(0.38, 0.475), **kw)

# Iteration 5 -> 4
ax.annotate("", xy=(0.71, 0.42), xytext=(0.63, 0.42), 
            arrowprops=dict(arrowstyle="-|>", lw=2, color='#E74C3C', connectionstyle="arc3,rad=-0.3"))
ax.text(0.67, 0.35, "Re-evaluasi", ha='center', va='center', fontsize=9, color='#E74C3C', style='italic')

# Iteration 2 -> 1
ax.annotate("", xy=(0.3, 0.72), xytext=(0.38, 0.72), 
            arrowprops=dict(arrowstyle="-|>", lw=2, color='#E74C3C', connectionstyle="arc3,rad=-0.3"))

ax.set_title("Diagram Alir Analisis Data (CRISP-DM)", fontsize=16, fontweight='bold', color='#2C3E50', y=0.95)

plt.savefig('output/00_flowchart_crispdm.png', facecolor='white', bbox_inches='tight', dpi=300)
plt.close()
print("Flowchart berhasil dibuat.")
