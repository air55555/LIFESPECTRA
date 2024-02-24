import hylite
from hylite import io
import matplotlib.pyplot as plt
import time


lib = io.load( 'test_data\library.csv' )
lib.quick_plot()

image = io.load( 'test_data\image.hdr' )
image.quick_plot(hylite.RGB)

cloud = io.load( 'test_data\hypercloud.ply' )
fig,ax = cloud.quick_plot('rgb', cloud.header.get_camera(0), fill_holes=True)
fig.show()
#plt.ioff() #wait for user close

# plot image and associated spectra
pixels = [(50,30), (150,30), (160,30)]


fig,ax = plt.subplots(1,2,figsize=(18,5))
image.quick_plot(hylite.SWIR, ax=ax[0], ticks=True) # plot image to existing axes object, and plot x- and y- coords
ax[0].scatter([p[0] for p in pixels], [p[1] for p in pixels], color=['r','g','b'])

# add a spectral caterpillar
image.plot_spectra(band_range=(2100.,2400.), indices=pixels, colours=['r','g','b'], ax=ax[1])
plt.show()

#cloud.quick_plot( cloud.header.get_camera(0), hylite.RGB)