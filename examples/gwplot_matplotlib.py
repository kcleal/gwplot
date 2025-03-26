from gwplot import Gw
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('_mpl-gallery')

# Initialize with reference genome
gw = Gw("hg19", theme="igv", canvas_width=2048, canvas_height=600)

# Add data sources
gw.add_bam("https://github.com/kcleal/gw/releases/download/v1.0.0/demo1.bam")
gw.add_region("chr8", 37047270, 37055161)
gw.set_font_size(18)
# Get the visualization as a NumPy array
img_array = gw.draw().array()

# Create the figure with 2 subplots vertically stacked
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))


# Display the gwplot visualization in the top subplot
ax1.imshow(img_array)
ax1.set_title('gwplot chr8:37047270-37055161')
ax1.axis('off')

# Create the matplotlib plot in the bottom subplot
x = np.linspace(0, 10, 100)
y = 4 + 1 * np.sin(2 * x)
x2 = np.linspace(0, 10, 25)
y2 = 4 + 1 * np.sin(2 * x2)

ax2.plot(x2, y2 + 2.5, 'x', markeredgewidth=2)
ax2.plot(x, y, linewidth=2.0)
ax2.plot(x2, y2 - 2.5, 'o-', linewidth=2)

ax2.set(xlim=(0, 8), xticks=np.arange(1, 8),
       ylim=(0, 8), yticks=np.arange(1, 8))

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()