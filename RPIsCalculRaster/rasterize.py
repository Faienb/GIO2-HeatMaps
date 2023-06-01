import rasterio
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import MergeAlg
from rasterio.plot import show
from numpy import int16
import numpy as np
import pyproj
from pyproj import Transformer

bbox_lon_min = 5.40
bbox_lat_min = 45.40
bbox_lon_max = 5.60
bbox_lat_max = 45.60

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

def rasterize(gpx_file, gpkg_file, geojson_file, output_raster_filename):
    # Créer le fichier raster de sortie
    
    # raster = gdal.GetDriverByName("GTiff")
    # out_raster_ds = raster.Create(output_raster_filename, 256, 256, 1, gdal.GDT_Byte)
    # out_raster_ds.SetGeoTransform((bbox_lon_min, (bbox_lon_max - bbox_lon_min) / 256, 0, bbox_lat_max, 0, -(bbox_lat_max - bbox_lat_min) / 256))
    out_raster_ds = 'temp'
    
    # Open example raster
    raster = rasterio.open('raster_total.tif')
    
    rasterize_gpx = gpx_to_raster(gpx_file,raster,output_raster_filename)
    # rasterize_geojson = geojson_to_raster(geojson_file,raster,output_raster_filename)

    rasterize_gpkg = gpkg_to_raster(gpkg_file,raster,output_raster_filename)
    
    # Définir la légende des couleurs
    # color_table = gdal.ColorTable()
    # color_table.SetColorEntry(0, (0, 0, 0, 0))  # Définir la couleur pour la valeur 0
    # color_table.SetColorEntry(255, (255, 0, 0, 255))  # Définir la couleur pour la valeur 1
    
    # band = out_raster_ds.GetRasterBand(1).ReadAsArray()
    # out_raster_ds.GetRasterBand(1).SetColorTable(color_table)
    
    # print(band)
    # print(rasterize_gpx)
    
    
    raster_final = rasterize_gpx + rasterize_gpkg
    
    # Plot raster
    fig, ax = plt.subplots(1, figsize = (10, 10))
    show(raster_final, ax = ax)
    plt.gca().invert_yaxis()
    
    
    return 

def gpkg_to_raster(gpkg_file, raster,output_raster_file):
   
    # Read in vector
    vector = gpd.read_file(gpkg_file)

    # Get list of geometries for all features in vector file
    geom = [shapes for shapes in vector.geometry]
     

    # Rasterize vector using the shape and coordinate system of the raster
    rasterized = features.rasterize(geom,
                                    out_shape = raster.shape,
                                    fill = 0,
                                    out = None,
                                    transform = raster.transform,
                                    all_touched = False,
                                    default_value = 1,
                                    dtype = None)
    
    # Plot raster
    fig, ax = plt.subplots(1, figsize = (10, 10))
    show(rasterized, ax = ax)
    plt.gca().invert_yaxis()
    
    return rasterized
    
def gpx_to_raster(gpx_file, raster, output_raster_file):
    
    raster_array = np.zeros((256,256))

    for i in gpx_file : 
        # Read in vector
        print('gpx\\'+i)
        vector = gpd.read_file('gpx\\'+i, layer='tracks')
    
        # Get list of geometries for all features in vector file
        geom = [shapes for shapes in vector.geometry]
        print(geom)
        # Rasterize vector using the shape and coordinate system of the raster
        rasterized = features.rasterize(geom,
                                        out_shape = raster.shape,
                                        fill = 0,
                                        out = None,
                                        transform = raster.transform,
                                        all_touched = False,
                                        default_value = 1,
                                        dtype = None,
                                        merge_alg=MergeAlg.add)
        raster_array = raster_array + rasterized
    


    return raster_array

def geojson_to_raster(json_file, raster, output_raster_file):
    
    raster_array = np.zeros((256,256))

    for i in json_file : 
        # Read in vector
        print('json\\'+i)
        vector = gpd.read_file('json\\'+i)
    
        # Get list of geometries for all features in vector file
        geom = [shapes for shapes in vector.geometry]
        
        # Rasterize vector using the shape and coordinate system of the raster
        rasterized = features.rasterize(geom,
                                        out_shape = raster.shape,
                                        fill = 0,
                                        out = None,
                                        transform = raster.transform,
                                        all_touched = False,
                                        default_value = 1,
                                        dtype = None,
                                        merge_alg=MergeAlg.add)
        raster_array = raster_array + rasterized
    
    # Plot raster
    fig, ax = plt.subplots(1, figsize = (10, 10))
    show(raster_array, ax = ax)
    plt.gca().invert_yaxis()

    return raster_array


