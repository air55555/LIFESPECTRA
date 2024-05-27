# -*- coding: utf-8 -*-
"""MY_WORK02_Data_projection_and_alignment.ipynb

"""

# download demo dataset
#!gdown 1X8xR1LxB7VR_JuvdmDwqJXeSILr9LP-n
#!unzip demo_data.zip

#from IPython.display import clear_output
#clear_output() # clear output (it isn't easy being clean!)

# install hylite
#! pip install git+https://github.com/hifexplo/hylite.git
# clear output (it isn't easy being clean!)
#clear_output()

"""**Importing Libraries**"""

from utils import  get_project_root
ROOT_DIR = str(get_project_root())+"\\BlackAngel\\"
from hylite import io
import numpy as np
import matplotlib.pyplot as plt
print (ROOT_DIR)

#%matplotlib inline

"""### From image to cloud, and visa versa

One of the main purposes of hylite is to facilitate the projection of point cloud attributes onto hyperspectral images, and the back-projection of hyperspectral image data onto point clouds to derive georeferenced 3-D hyperclouds.

The following notebook outlines the various ways that data can be moved between these data structures, and finishes by showing how the position of an image can be located relative to a georeferenced point cloud using computer vision techniques.

### 1. Cloud to image

Moving data from point clouds onto an image is a standard computer graphics operation, known as rendering. This can be used to create images of e.g. surface orientation or position (both very useful properties for e.g. topographic corrections).
"""

# load a point cloud dataset
cloud = io.load( ROOT_DIR+'test_data1\hypercloud.ply' )
cloud.decompress() # this was compressed from float to integer to save space; so we need to convert it back

cam = cloud.header.get_camera(0) # get the camera pose used for rendering (more on this later)

fig,ax = cloud.quick_plot('rgb', cam, fill_holes=True)

fig.show()

# create images with different cloud attributes in them
attr = [
    'rgb', # cloud RGB
    'klm', # cloud normals
    'xyz', # point positions
    (0,25,40), # cloud attributes [ in this case, these will be hyperspectral bands as this is a hypercloud ]
]
images = []
for a in attr:
    images.append( cloud.render( cam, a, s=1,  fill_holes=True)) # N.B. adjust 's' to change the point size

from hylite import HyImage
#HyImage.quick_plot?

images[0].quick_plot

# plot
fig,ax = plt.subplots(2,2,figsize=(18,10))
for i,a,t in zip(images,ax.ravel(),attr):
    i.set_as_nan(0) # replace background with nan
    i.quick_plot((0,1,2), ax=a,
                 vmin=2, vmax=98, # as these are integers, they will be treated as percentile clip values.
                 tscale=True) #N.B. tscale=True means each band is scaled separately for visualising.
    a.set_title(t)
fig.tight_layout()
fig.show()

"""These rendered attributes can then be used to calculate other important properties, e.g. the target - sensor distance for each pixel in a hyperspectral scene:"""

depths = cloud.render(cam, bands='xyz',fill_holes=True ) # render point position
depths.set_as_nan(0) # remove zeros
depths.data -= cam.pos # put camera at origin
depths.data = np.dstack( [ depths.data , np.linalg.norm(depths.data, axis=-1 ) ] ) # compute distance from sensor
depths.set_band_names(['x','y','z','depth']) # add band names

# plot depth
fig,ax = depths.quick_plot('depth')
fig.colorbar(ax.cbar) # N.B. colorbar information is added to the relevant axes object as the .cbar attribute
fig.show()

"""### 2. Image to cloud

Similarly, the *project(...)* function can be used to back-project image data onto a point cloud.
"""

image = images[0].copy() # pretend this is some fancy hyperspectral sensor data
image.data = 1-image.data

cloud.data = None # clear previous data [ otherwise bands would be appended ]
cloud.project( image, cam, bands=(0,1,2),trim=False ) # project bands 0, 1 and 2 onto the point cloud
print(cloud.data.shape) # data has now been projected onto the point clouds

fig,ax = cloud.quick_plot((0,1,2), cloud.header.get_camera(0), s=1 )
fig.show()

"""### Locating sensor position

The above methods only work if the sensor position and orientation are known. While this could theoretically be measured, it is challenging to do accurately. Instead, *hylite* provides two keypoint based methods for solving camera position.

The first of these uses manually selected keypoint pairs to associate real-world coordinates with >4 image pixels and thus solve the sensor position and orientation. Note that: (1) image dimensions and sensor FOV must be known in advance, though these are generally reported by sensor manufacturers, and (2) lens distortions should be corrected prior to applying this alignment.
"""

image2 = io.load(ROOT_DIR+'test_data1\scene.jpg')
fig,ax = plt.subplots(figsize=(5,5))
image2.quick_plot((0,1,2),ax=ax)
fig.show()

"""##### Manual matching

CloudCompare can be used to interactively select points in the point cloud and get the indices of points representing features identifyable in the image:
"""

# keypoints as cloud IDs
points = np.array([137168, 64179, 194030, 38452, 18604,
                  169834, 208316, 217343, 217344, 250920, 318733, ] )

# keypoints as image pixel coordinates
pixels = [(196,225),(202,251),(63,222),(215,319),(257,301),
          (138,178),(46,185),(220,166),(348,170),(317,195),(359,211)]

# define new camera object to store results in (and define sensor properties)
from hylite.project import Camera
cam2 = Camera(np.zeros(3), np.zeros(3),
             'pano', # this is a tripod-mounted (panoroamic) sensor. Set to 'persp' for frame sensors.
             fov = 32.3, # vertical sensor field of view
             dims = (image2.xdim(), image2.ydim()),
             step = 0.084 # angular step [ provided by manufacture, or assume square pixels ]
             )

from hylite.project.align import align_to_cloud_manual
est, r = align_to_cloud_manual( cloud, cam2, points, pixels) # solve camera pose using PnP solution
print('Aligned camera with %.1f pixel residual.' % r)

fig,ax = plt.subplots(1,2,figsize=(12,10))
image2.quick_plot((0,1,2),ax=ax[0])
cloud.quick_plot('rgb', est, ax=ax[1])
ax[0].set_title("Image")
ax[1].set_title("View from estimated camera")
for px,py in pixels:
    ax[0].scatter(px,py)
    ax[1].scatter(px,py)
for a in ax:
    a.set_ylim(350,100) # zoom in a bit
fig.tight_layout()
fig.show()

# """##### Automated matching
#
# If an estimated camera position is available, e.g. using field measurements or by visualising the point-cloud in CloudCompare and noting the approximate camera position and orientation (hylite uses the same Euler angle scheme as CloudCompare for representing orientations) then automatic matching techniques (SIFT or ORB) can be used to match keypoints between the (rendered) point cloud and the image.
#
# This can be a fiddly process, but when it works it can greatly improve the accuracy with which sensor pose can be estimated. In the following we use this technique to refine our initial estimate of the camera pose.
# """
#
# from hylite.project.align import align_to_cloud
# est2, kp, r = align_to_cloud( image2, cloud, est, bands=(0,1,2),
#                              method='sift', # which keypoint extractor to use
#                              sf=2, # supersample rendered point cloud to improve matching (sometimes)
#                              s=2, # size of points when rendering cloud
#                              recurse=1, # repeatedly render cloud to improve/update matching based on new pose
#                              gf=True) # display graphical QAQC plots
#
# fig,ax = plt.subplots(1,2,figsize=(12,10))
# image2.quick_plot((0,1,2),ax=ax[0])
# cloud.quick_plot('rgb', est2, ax=ax[1])
# ax[0].set_title("Image")
# ax[1].set_title("View from aligned camera")
# for a in ax:
#     a.set_ylim(350,100) # zoom in a bit
# fig.tight_layout()
# fig.show()

"""### HyScene objects

To facilitate fusing clouds and images and manage associated datasets (e.g. per-pixel depths) hylite has a special type of *HyCollection* specifically for a coregistered image-cloud pair. These can facilitate e.g. illumination correction or hypercloud projection workflows.
"""

from hylite import HyScene

S = HyScene('myscene', './outputs/') # initialise a scene just like any HyCollection
S.construct( image2, cloud, est ) # do projections and construct scene

S.print()

# plot per-pixel depths
plt.imshow( S.depth.T, cmap='gray')
plt.show()

# project image data to cloud
cloud2 = S.push_to_cloud( (0,1,2), method='average' )

fig,ax = cloud2.quick_plot( (0,1,2), 'ortho', s=4 )
fig.show()

S.save() # save HyScene for later use

io.save(ROOT_DIR+'content/cloud2.ply', cloud2)

