import rasterio
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import MergeAlg
import numpy as np


def get_file_names(folder_path):
    """
    Récupère le nom de tous les fichiers dans un dossier local.
    """
    file_names = []

    # Vérifier si le chemin spécifié est un dossier existant
    if os.path.isdir(folder_path):
        # Parcourir tous les fichiers dans le dossier
        for file_name in os.listdir(folder_path):
            # Vérifier si le chemin est un fichier (pas un dossier)
            if os.path.isfile(os.path.join(folder_path, file_name)):
                file_names.append(file_name)
    else:
        print(f"Erreur: Le dossier spécifié n'existe pas : {folder_path}")

    return file_names

def rasterize(gpx_file, gpkg_file, geojson_file, bbox_lon_min,bbox_lat_min,bbox_lon_max,bbox_lat_max):
    
    # Transformation affine
    xsize = (bbox_lon_max - bbox_lon_min) / 256
    ysize = (bbox_lat_max - bbox_lat_min) / 256 

    transfo = rasterio.transform.from_origin(bbox_lon_min, bbox_lat_max, xsize, ysize)
    
    # Calcul des rasters array en fonction du format des traces
    raster_gpx = gpx_to_raster(gpx_file,transfo)
    # raster_gpkg = gpkg_to_raster(gpkg_file,transfo)
        
    # Calcul du raster final 
    # raster_final = raster_gpx + raster_gpkg
    raster_final = raster_gpx
    # Plot raster
    # fig, ax = plt.subplots(1, figsize = (10, 10))
    # show(raster_final, ax = ax)
    
    return raster_final

def gpkg_to_raster(gpkg_file, raster):
   
    # Read in vector
    vector = gpd.read_file(gpkg_file)

    # Get list of geometries for all features in vector file
    geom = [shapes for shapes in vector.geometry]
     

    # Rasterize vector using the shape and coordinate system of the raster
    rasterized = features.rasterize(geom,
                                    out_shape = (256,256),
                                    fill = 0,
                                    out = None,
                                    transform = raster,
                                    all_touched = False,
                                    default_value = 1,
                                    dtype = None)
    
    return rasterized
    
def gpx_to_raster(gpx_file, raster):
    
    raster_array = np.zeros((256,256))

    for i in gpx_file : 
        # Read in vector
        vector = gpd.read_file('gpx\\'+i, layer='tracks')
    
        # Get list of geometries for all features in vector file
        geom = [shapes for shapes in vector.geometry]
        
        # Rasterize vector using the shape and coordinate system of the raster
        rasterized = features.rasterize(geom,
                                        out_shape = (256,256),
                                        fill = 0,
                                        out = None,
                                        transform = raster,
                                        all_touched = False,
                                        default_value = 1,
                                        dtype = None,
                                        merge_alg=MergeAlg.add)
        raster_array = raster_array + rasterized
    


    return raster_array


