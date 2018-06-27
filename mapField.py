
from shapely.geometry.polygon import Polygon 
from shapely.ops import polygonize
from shapely.geometry import mapping, LineString, MultiLineString,CAP_STYLE,JOIN_STYLE,Polygon
from shapely.affinity import rotate,affine_transform,translate
import numpy as np
from matplotlib import pyplot as plt
import math
import csv

import fiona
from fiona.crs import from_epsg

def grid_dim(x,y,dx,dy,matrix):
    
    affine = (matrix[0:2]+matrix[3:5]+matrix[2:3]+matrix[5:6])
    
    x = np.linspace(0, x, dx+1)
    y = np.linspace(0, y, dy+1)

    hlines = [((x1, yi), (x2, yi)) for x1, x2 in zip(x[:-1], x[1:]) for yi in y]
    
    h_trans = [affine_transform(LineString(i),affine) for i in hlines]
    
    vlines = [((xi, y1), (xi, y2)) for y1, y2 in zip(y[:-1], y[1:]) for xi in x]
    
    v_trans = [affine_transform(LineString(i),affine) for i in vlines ]
    
    agrid = MultiLineString(v_trans+h_trans)
    ngrid = MultiLineString(vlines+hlines)
       
    return ngrid,agrid

def plot_grid(grid,title='Test'):
   
    grid = grid_dim()
    grid = rotate(grid,angle)
   
    fig,ax = plt.subplots(figsize=(10,10))
    for line in grid:
        x,y = line.xy
        img1 = ax.plot(x,y,color='#000000')
   
    ax.set_title(title,color='#FFFFFF')
    ax.set_axis_on()
    plt.show()

def rot_plots(grid,distance,angle,xo,yo,matrix):
    polygons = list()
    
    affine = (matrix[0:2]+matrix[3:5]+matrix[2:3]+matrix[5:6])
    
    t_grid = translate(grid,xo,yo)
    r_grid = rotate(t_grid,angle,origin=(xo,yo))
    
    plots = list(polygonize(r_grid))
    
    tp = [Polygon(pi) for pi in plots]
    
    for poly in tp:
        polygons.append(poly.buffer(-(distance),
                                 resolution = 1,
                                 cap_style=3,
                                 join_style=2,
                                 mitre_limit=10)) 
    
    affine_polygons = list()
    for i in polygons:
        affine_polygons.append(affine_transform(i,affine))
        
    return affine_polygons,polygons


def plot_buffer(polygons,grid):
   
    fig, ax = plt.subplots(figsize = (10,10))
   
       
    for poly in polygons:
        x,y = poly.exterior.xy
        ax.plot(x,y,color='#6699cc')
        ax.fill(x, y, alpha=0.3, fc='r', ec='none')
   
    ax.set_title('Test',color='#FFFFFF')
    ax.set_axis_on()
   
   
def read_csv(in_csv,index_name):
    data = {}
    data[index_name] = []
    with open(in_csv) as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            data[index_name].append(line[0])
    return data
           
def write_shapes(poly,grid,out_dest,index_name,data):
    c,d=0,1
    schema = {"geometry": "Polygon","properties": {"id": "int",index_name : 'str' }, }
   
    with fiona.open(out_dest, 'w', driver='GeoJSON',schema=schema, crs=('EPSG:32631')) as ds_dst:
        c,d=0,0
        for i in poly:
            ds_dst.write({'geometry': mapping(i), 
                         'properties': {'id': c,
                         index_name:data.get(index_name)[c]},
                        })  
            c+=1
            
# Function to define, save field plot polygons to a raster file

def makeGrid(x,y,dx,dy,xo,yo,distance,angle,matrix,out_dest,index_name,in_csv):
   
    grid,agrid = grid_dim(x,y,dx,dy,matrix)
    apoly,poly = rot_plots(grid,distance,angle,xo,yo,matrix) 
    data = read_csv(in_csv,index_name)
    #write_shapes(apoly,agrid,out_dest,index_name,data)
    #plt_polygons = plot_buffer(poly,agrid)
   
    return apoly,poly