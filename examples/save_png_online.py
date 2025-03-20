from gwplot import Gw

# Initialize with reference genome
gw = Gw("hg19")

# Add data sources
gw.add_bam("https://github.com/kcleal/gw/releases/download/v1.0.0/demo1.bam")
gw.add_track("https://github.com/kcleal/gw/releases/download/v1.0.0/demo1.vcf")

# Set region to view
gw.add_region("chr8", 37047270, 37055161)

# Render and save
gw.draw()
gw.save_png("output_online.png")
