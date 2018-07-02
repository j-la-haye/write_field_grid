# write_field_grid
The following Repository contains two scripts, makeGrid and visualizeGrid that are designed to 
map plot polygons to an input geoTiff ortho-photo and automatically generate a polygon shapefile
that contains the zonal statistics of an input NDVI orthophoto. 


makeGrid take field dimensions and plot division arguments as input and creates a georeferenced polygon shapefile that can 
be overlayed on an input ortho-photo. 

visualizeGrid - takes the output of makeGrid as input and overlays it on an input NDVI ortho-photo that is calculated from 
an input red and NIR geoTiff orthophoto. Zonal-statistics are then calculated by the overlaid polygon shapefile and written
to the shapefile as attributes. The script then displays the results of the zonal statistic calculation in an interactive plot. 
