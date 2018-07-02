
from shapely.geometry.polygon import Polygon 
from shapely.ops import polygonize
from shapely.geometry import (mapping,shape,LineString,
                              MultiLineString,CAP_STYLE,JOIN_STYLE,Polygon)
from shapely.affinity import rotate,affine_transform,translate
import numpy as np
from matplotlib import pyplot as plt
import csv
import fiona
from rasterstats import zonal_stats
from collections import OrderedDict
import geopandas as gpd
import os



def grid_dim(x,y,dx,dy,matrix):
    
    affine = (matrix[0:2]+matrix[3:5]+matrix[2:3]+matrix[5:6])
    
    x = np.linspace(0, x, dx+1)
    y = np.linspace(0, y, dy+1)

    hlines = [((x1, yi), (x2, yi)) for x1, x2 in zip(x[:-1], x[1:]) for yi in y]
    
    h_trans = [affine_transform(LineString(i),affine) for i in hlines]
    
    vlines = [((xi, y1), (xi, y2)) for y1, y2 in zip(y[:-1], y[1:]) for xi in x]
    
    v_trans = [affine_transform(LineString(i),affine) for i in vlines ]
    
    agrid = MultiLineString(v_trans+h_trans)
    ngrid = MultiLineString(hlines+vlines)
       
    return ngrid,agrid

def plot_grid(grid,angle,title='Test'):
   
    grid = rotate(grid,angle)
   
    fig,ax = plt.subplots(figsize=(10,10))
    for line in grid:
        x,y = line.xy
        img1 = ax.plot(x,y,color='black')
   
    ax.set_title(title,color='grey')
    ax.tick_params(axis='x', colors='grey')
    ax.tick_params(axis='y', colors='grey')
    ax.set_axis_on()
    #plt.savefig('Results/plot_grid.png',dpi=300)
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
        
    return affine_polygons,polygons,r_grid


def plot_buffer(polygons,grid,title):
   
    fig, ax = plt.subplots(figsize = (10,10))
   
    for line in grid:
        x,y = line.xy
        img1 = ax.plot(x,y,color='black')
    
    for poly in polygons:
        x,y = poly.exterior.xy
        ax.plot(x,y,color='#6699cc')
        ax.fill(x, y, alpha=0.3, fc='r', ec='none')
   
    ax.set_title(title,color='grey')
    ax.tick_params(axis='x', colors='grey')
    ax.tick_params(axis='y', colors='grey')
    ax.set_axis_on()
    #plt.savefig('Results/plot_buffer.png',dpi=300)

def read_csv(in_csv,index_name):
    data = {}
    c=0
    while c < 1:
        for col in index_name:
            data[col] = []
            with open(in_csv) as f:
                reader = csv.reader(f)
                next(reader)
                for line in reader:
                    data[col].append(line[c])
                c+=1
    return data
           
def write_shapes(poly,out_dest,in_csv,index_name):
    
    try:
        os.remove(out_dest)
    
    except OSError:
        pass
    
    data = read_csv(in_csv,index_name)
    #schema = {"geometry": "Polygon","properties": {"id": "int",{index_name} : 'str' }, }
    schema =  {'geometry': 'Polygon',
               'properties': {}} 
    for i in index_name:
        schema['properties'][i] = 'str'
    
    with fiona.open(out_dest, 'w', driver='GeoJSON',schema=schema, crs=('EPSG:32631')) as ds_dst:
        for i in range(len(poly)):
            prop = OrderedDict()
            #while i < len(poly)-1 :
            for key in data:
                prop.update({key:data.get(key)[i]})
            ds_dst.write({'geometry': mapping(poly[-(i+1)]),'properties': prop})      
                
                
def calc_zonal_stats(input_shapefile,input_raster,stats,output_shapefile):
    
    try:
        os.remove(output_shapefile)
    except OSError:
        pass
    
    raster=input_raster
    with fiona.open(input_shapefile, 'r') as poly:
        
        schema = poly.schema.copy()
        zs = zonal_stats(poly,raster,stats=stats)
        input_crs = poly.crs

        schema['geometry'] = 'Polygon'

        stats = stats
        for i in stats:
            schema['properties'][i] = 'str'

        with fiona.open(output_shapefile, 'w', 'GeoJSON', schema, input_crs) as output:
            c=0
            for i in poly:
                prop = OrderedDict()
                for key in zs[c]:
                    prop.update({key:round(zs[c][key],2)})
                i['properties'].update(prop)
                output.write({'properties':i['properties'],'geometry': mapping(shape(i['geometry']))})
    
    data = gpd.read_file(output_shapefile)
    dt = data.head(n=len(data))
    return prop,dt


# Function to define, save field plot polygons to a raster file

def makeGrid(x,y,dx,dy,xo,yo,distance,angle,matrix,out_dest,in_csv,index_name):
   
    grid,agrid = grid_dim(x,y,dx,dy,matrix)
    apoly,poly,grid = rot_plots(grid,distance,angle,xo,yo,matrix) 
    #write_shapes(apoly,out_dest,in_csv,index_name)
    #plt_polygons = plot_buffer(poly,agrid)
   
    return apoly,poly