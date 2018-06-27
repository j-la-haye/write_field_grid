
from shapely.geometry.polygon import Polygon
from shapely.ops import polygonize,polygonize_full
from shapely.geometry import mapping, LineString, MultiLineString, MultiPolygon,CAP_STYLE,JOIN_STYLE,shape


import rasterio
from rasterio.plot import show as show
import numpy as np
from descartes import PolygonPatch

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection

import mapField
#from mapField import plot_buffer as plot_buffer
#from mapField import plot_grid as plot_grid
from mapField import makeGrid as makeGrid
#from mapField import rot_plots as rot_plots
#from mapField import grid_dim as grid_dim

import fiona

def read_bands(red,nir):
    
    with rasterio.open(red) as red:
        RED = red.read()
    with rasterio.open(nir) as nir:
        NIR = nir.read()

    #compute the ndvi band and write to tif
    np.seterr(divide='ignore', invalid='ignore')

    ndvi = (NIR.astype(float)-RED.astype(float))/(NIR+RED)
    ndvi[ ndvi == 0] = np.nan
    ndvi[ndvi < 0] = 0
   
    outfile='Bands/ndvi.tif'
    profile = red.meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)
    profile.update(nodata = 0)

    with rasterio.open(outfile, 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32))
    
    with rasterio.open(outfile) as src:
        ndvi = src.read()
        bounds = src.bounds
        transform = src.transform
        crs = src.crs
        affine = src.affine
        transform = src.transform
        #ndvi[ ndvi == 0] = np.nan
        #ndvi[ndvi < 0] = 0
    
    fig,ax = plt.subplots(figsize=(10,10))

    ax.set_xticks(np.around(np.arange(0,7000,500),0))
    ax.set_yticks(np.around(np.arange(0,7000,500),0))
    ax.set_aspect(1)
    ax.set_axis_on()
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    plt.title("NDVI Band",color='#FFFFFF')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    show(ndvi,ax,cmap='RdYlGn')
    
    return ndvi,affine
            
def aoi_zoom(minx,maxx,miny,maxy,img):
    
    img[ img == 0] = np.nan
    img[img < 0] = 0
   
    
    fig,ax = plt.subplots(figsize=(12,12))

    w, h = maxx - minx, maxy - miny
    ax.set_ylim(maxy + 0.01 * h, miny - 0.01 * h)
    ax.set_xlim(minx - 0.01* w, maxx + 0.01 * w)
        
    ax.set_xticks(np.around(np.arange(minx - 0.01 * w, maxx + 0.01 * w, 30),0))
    ax.set_yticks(np.around(np.arange(miny - 0.01 * h, maxy + 0.01 * h, 30),0))
    ax.set_aspect(1)
    plt.xticks(rotation=45,horizontalalignment='right')
    ax.grid(b=True, which='major', color='w', linewidth=0.8)
    ax.grid(b=True, which='minor', color='w', linewidth=0.5)
    ax.set_axis_on()
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    plt.title("NDVI Band",color='#FFFFFF')
    show(img,ax,cmap='RdYlGn')
    
    return minx,maxx,miny,maxy,img

def plot_grid(multi_polygon,img):
    
    mp=MultiPolygon([feature for feature in multi_polygon])
    patches=[PolygonPatch(feature, edgecolor="#FFFFFF", facecolor="#555555", linewidth=2) 
            for feature in multi_polygon]

    fig,ax = plt.subplots(figsize=(10,10))

    cm = plt.get_cmap('RdBu')
    num_colours = len(mp)
    
    minx, miny, maxx, maxy = mp.bounds
    print(mp.bounds)
    
    w, h = maxx - minx, maxy - miny
    ax.set_ylim(maxy + 0.1 * h, miny - 0.1 * h)
    ax.set_xlim(minx - 0.1 * w, maxx + 0.1 * w)
    
    ax.set_aspect(1)

    patches = []
    for idx, p in enumerate(mp):
        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#5FFF5F', alpha=0.75, zorder=1))


    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_axis_on()
    ax.set_xticks(np.around(np.arange(minx - 0.1 * w, maxx + 0.1 * w, 30),0))
    ax.set_yticks(np.around(np.arange(miny - 0.1 * h ,maxy + 0.1 * h, 30),0))
    ax.tick_params('both',pad=15)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    plt.xticks(rotation=45,horizontalalignment='right')
    ax.grid(b=True, which='major', color='w', linewidth=0.8)
    ax.grid(b=True, which='minor', color='w', linewidth=0.5)
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    plt.title("Shapefile",color='#FFFFFF')
    show(img,ax, cmap='RdYlGn')
    plt.show()