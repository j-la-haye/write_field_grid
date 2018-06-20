from shapely.geometry.polygon import Polygon 
from shapely.ops import polygonize
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, LineString, MultiLineString,CAP_STYLE, JOIN_STYLE
import plot_figures
from plot_figures import set_limits
from shapely.affinity import rotate,affine_transform,translate
import numpy as np
from matplotlib import pyplot as plt
import math
import csv

def grid_dim():
  
    x = np.linspace(minx, maxx, div_y+1)
    y = np.linspace(miny, maxy, div_x+1)

    hlines = [((x1, yi), (x2, yi)) for x1, x2 in zip(x[:-1], x[1:]) for yi in y]
    vlines = [((xi, y1), (xi, y2)) for y1, y2 in zip(y[:-1], y[1:]) for xi in x]
    grid = MultiLineString(hlines+vlines)
    
    return grid

def plot_grid(fig_x,fig_y,title='Test'):
    
    #grid = grid_dim()
    
    grid = rotate(grid_dim(),angle)
    
    fig,ax = plt.subplots(figsize=(fig_x,fig_y))
    for line in grid:
        x,y = line.xy
        img1 = ax.plot(x,y,color='#000000')
    
    ax.set_title(title,color='#FFFFFF')
    ax.set_axis_on()
    #set_limits(ax,minx,maxx,miny,maxy)
    plt.show()
    

def rotate_plots(angle,distance=0,fig_x=10,fig_y=10,title='Test'):
    bufs = []
    grid = grid_dim()
    
    t_grid = translate(grid,xo,yo)
    r_grid = rotate(t_grid,angle,origin =(xo,yo))
    r_plots = list(polygonize(r_grid))
    
    for poly in r_plots:
        buf = poly.buffer(-(distance),resolution=1,cap_style=3,join_style=2,mitre_limit=10)
        bufs.append(buf)
    
    ######## Plot Grid Lines Only
    #
    #fig,ax = plt.subplots(figsize=(fig_x,fig_y))
    #ax.set_title(title,color='#FFFFFF')
    #bufs=[]
    #fp=[]
    # Plot Grid Lines
    #for line in r_grid:
    #    x,y = line.xy
    #    ax.plot(x,y,color='#000000')   
    
    ####### Plot field polygons
    #
    #for poly in r_plots:
    #    x,y=poly.exterior.xy
    #   img1 = ax.plot(x, y,color='#000000')
    #    ax.fill(x, y, alpha=0.3, fc='r',color='#6699cc', ec='none')    
    #    ax.set_title(title,color='#FFFFFF')
    polys = polygonize(bufs)
    
    #plt.show()  
    return bufs,r_grid


def plot_buffer(title='Test'):
    fig, ax = plt.subplots(figsize = (10,10))
    
    bufs,grid=rotate_plots(angle,buffer)
    
    
    for line in grid:
        x,y = line.xy
        ax.plot(x,y,color='#000000')
        
    for fld in bufs:
        x,y = fld.exterior.xy
        ax.plot(x,y,color='#6699cc')
        ax.fill(x, y, alpha=0.3, fc='r', ec='none')
    
    ax.set_title(title,color='#FFFFFF')
    ax.set_axis_on()
    
    #return bufs
    #plt.show()

def read_csv(in_csv):
    data = {}
    data['test_num'] = []
    with open(in_csv) as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            data['test_num'].append(line[0])
    return data
    
def write_shp(out_dest):

    out = out_dest
    schema = {
        "geometry": "Polygon",
        "properties": {"id": "int",
                       "test_num" : 'str' } 
    }
    plots,grid = rotate_plots(buffer,angle)
    c = 0
    with fiona.open(out, 'w', driver='ESRI Shapefile',schema=schema, crs=('EPSG:32631')) as ds_dst:
        indices = read_csv(in_csv)
        for poly in plots:
            ds_dst.write({'geometry': mapping(poly), 
                          'properties': {'id': c,
                          'test_num':indices.get('test_num')[c]},
                         })
            
            c+=1
            
               
if __name__ == '__main__':
    
    div_y = 1
    div_x = 18
    minx, miny, maxx, maxy = 0,0,15,60
    title = 'Test'
    fig_x = 10
    fig_y = 10
    angle = 75
    buffer = 0.5
    xo,yo = 584435,5696135
    in_csv = 'test.csv'
    
    field = plot_grid(fig_x,fig_y)
    plots = plot_buffer('Test_Plots')
    shape = write_shp('/Users/jesselahaye/Documents/gisTools/Tier_1/test_plot6.shp')