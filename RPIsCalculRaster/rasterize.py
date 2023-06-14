import rasterio
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import MergeAlg
import numpy as np


def get_file_names(folder_path):
    """
    Récupère le nom de tous les fichiers d'un dossier local.
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

def rasterize(tracks_folder_path, bbox_lon_min,bbox_lat_min,bbox_lon_max,bbox_lat_max, pass_openstreetmap):
    
    # Transformation affine
    xsize = (bbox_lon_max - bbox_lon_min) / 256
    ysize = (bbox_lat_max - bbox_lat_min) / 256 

    transfo = rasterio.transform.from_origin(bbox_lon_min, bbox_lat_max, xsize, ysize)
    
    file_names = get_file_names(tracks_folder_path)
    
    lst_raster_array = []
    
    for file in file_names : 
        ext = file.split('.')[1]
        if ext == 'gpx' : 
            raster_gpx = gpx_to_raster(tracks_folder_path, file, transfo)
            lst_raster_array.append(raster_gpx)
        elif ext == 'gpkg':
            raster_gpkg = gpkg_to_raster(tracks_folder_path, file, transfo)
            lst_raster_array.append(raster_gpkg)
        else :
            print(f'Extension {ext} not available')
        
    
    raster_final = np.zeros((256,256))
    for raster in lst_raster_array :
        raster_final += raster

            
    # # Calcul des rasters array en fonction du format des traces
    # raster_gpx = gpx_to_raster(gpx_file,transfo)
    # if pass_openstreetmap != True : 
    #     raster_gpkg = gpkg_to_raster(gpkg_file,transfo)
        
    #     # Calcul du raster final 
    #     raster_final = raster_gpx + raster_gpkg
    # else : 
    #     # Calcul du raster final 
    #     raster_final = raster_gpx
    
    # Plot raster
    # fig, ax = plt.subplots(1, figsize = (10, 10))
    plt.imshow(raster_final)
    plt.show()
    
    return raster_final

def gpkg_to_raster(tracks_folder_path,gpkg_file, transfo):
   
    # Read in vector
    vector = gpd.read_file(tracks_folder_path+'\\'+gpkg_file)

    # Get list of geometries for all features in vector file
    geom = [shapes for shapes in vector.geometry]
     

    # Rasterize vector using the shape and coordinate system of the raster
    raster_array = features.rasterize(geom,
                                    out_shape = (256,256),
                                    fill = 0,
                                    out = None,
                                    transform = transfo,
                                    all_touched = False,
                                    default_value = 1,
                                    dtype = None)
    
    return raster_array
    
def gpx_to_raster(tracks_folder_path,filename,transfo):
    


    # Read in vector
    vector = gpd.read_file(tracks_folder_path+'\\'+filename, layer='tracks')

    # Get list of geometries for all features in vector file
    geom = [shapes for shapes in vector.geometry]
    
    # Rasterize vector using the shape and coordinate system of the raster
    raster_array = features.rasterize(geom,
                                    out_shape = (256,256),
                                    fill = 0,
                                    out = None,
                                    transform = transfo,
                                    all_touched = False,
                                    default_value = 1,
                                    dtype = None,
                                    merge_alg=MergeAlg.add)
    
    return raster_array


