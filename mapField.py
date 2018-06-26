
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
   
    #grid = grid_dim()
   
    #grid = rotate(grid,angle)
   
    fig,ax = plt.subplots(figsize=(10,10))
    for line in grid:
        x,y = line.xy
        img1 = ax.plot(x,y,color='#000000')
   
    ax.set_title(title,color='#FFFFFF')
    ax.set_axis_on()
    #set_limits(ax,minx,maxx,miny,maxy)
    plt.show()

def rot_plots(grid,distance,angle,xo,yo,matrix):
    polygons = list()
    
    #affine = (matrix[1:3]+matrix[4:]+matrix[:1]+matrix[3:4])
    affine = (matrix[0:2]+matrix[3:5]+matrix[2:3]+matrix[5:6])
    
    t_grid = translate(grid,yo,xo)
    r_grid = rotate(t_grid,angle,origin = (yo,xo))
    
    plots = list(polygonize(r_grid))
    
    tp = [Polygon(pi) for pi in plots]
    #ap = [affine_transform(i,affine) for i in tp]
    
    for poly in tp:
        polygons.append(poly.buffer(-(distance),
                                 resolution = 1,
                                 cap_style=3,
                                 join_style=2,
                                 mitre_limit=10)) 
    
    test = list()
    for i in polygons:
        test.append(affine_transform(i,affine))
        
    return test,polygons

def rotate_plots(grid,distance,xo,yo):
    #polygons = []
    t_grid = translate(grid,yo,xo)
     
    r_grid = rotate(t_grid,angle,origin =(xo,yo))
   
    plots = polygonize(r_grid)
    
    t_poly = [Polygon(pi).buffer((-distance),resolution = 1,cap_style=3,join_style=2,mitre_limit=10) 
              for pi in plots]
    
    
    return t_poly,t_grid


def plot_buffer(polygons,grid):
   
    fig, ax = plt.subplots(figsize = (10,10))
   
    #for line in grid:
    #    x,y = line.xy
    #    ax.plot(x,y,color='#000000')
       
    for poly in polygons:
        x,y = poly.exterior.xy
        ax.plot(x,y,color='#6699cc')
        ax.fill(x, y, alpha=0.3, fc='r', ec='none')
   
    ax.set_title('Test',color='#FFFFFF')
    ax.set_axis_on()
   
   
def read_csv(in_csv):
    data = {}
    data['test_num'] = []
    with open(in_csv) as f:
        reader = csv.reader(f)
        next(reader)
        for line in reader:
            data['test_num'].append(line[0])
    return data
           
def write_shapes(poly,grid,out_dest,index_name,data):
    c,d=0,1
    schema = {"geometry": "Polygon","properties": {"id": "int",index_name : 'str' }, }
   
    with fiona.open(out_dest, 'w', driver='ESRI Shapefile',schema=schema, crs=('EPSG:32631')) as ds_dst:
        c,d=0,0
        for i in poly:
            ds_dst.write({'geometry': mapping(i), 
                         'properties': {'id': c,
                         'test_num':data.get('test_num')[c]},
                        })  
            c+=1
# Function to define
def makeGrid(x,y,dx,dy,xo,yo,distance,angle,matrix,out_dest,index_name,in_csv):
   
    grid,agrid = grid_dim(x,y,dx,dy,matrix)
    apoly,poly = rot_plots(grid,distance,angle,xo,yo,matrix) 
    data = read_csv(in_csv)
    write_shapes(apoly,agrid,out_dest,index_name,data)
    #plt_polygons = plot_buffer(poly,agrid)
   
    return poly,apoly