import requests
import osmnx as ox
import pyproj
from pyproj import Transformer
from bs4 import BeautifulSoup
import polyline
import numpy as np
import math
import rasterio
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import MergeAlg
from rasterio.plot import show
from numpy import int16
import rasterize as rz

bbox_lon_min = 5.40
bbox_lat_min = 45.40
bbox_lon_max = 5.60
bbox_lat_max = 45.60

options = {'utagawavtt':False,
           'tracegps':False,
           'openstreetmap':False,
           'camptocamp':False,
           'openrunner':False}

  
def num2deg(x_tile, y_tile, zoom):
    """
    return the NW-corner of the tile, Use x_tile+1, y_tile+1 to get the other corners
    """
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def get_track_in_bbox_Utagawavtt(lon_min, lat_min, lon_max, lat_max):
    page = 0
    lst_track = []
    while True:
        url = 'https://www.utagawavtt.com/searchAsync?w=[{},{},{},{}]&q=[1,2,3,4]&aa=25&x=0&u={}'.format(lon_min,lat_min,lon_max,lat_max,page)
        headers = { 'X-Requested-With': 'XMLHttpRequest','Referer': 'https://www.utagawavtt.com/'}
        rep = requests.get(url, headers=headers)
        out = rep.json()
        lst_track += out["results"]
        page = out['resultsMeta']['pager']['next']
        if page == 0:
            break
    print('Utagawavtt : {} tracks have been detected in bbox'.format(len(lst_track)))
    return lst_track

def get_one_track_Utagawavtt(id_track):
    url = 'https://www.utagawavtt.com/VTT/UTG-Topo-{}/utgtrack-{}.gpx'.format(id_track,id_track)
    
    # Envoyer la requête GET
    rep = requests.get(url)

    # Vérifier le code de statut de la réponse
    if rep.status_code == requests.codes.ok:
        # Retourner le contenu de la réponse
        # Attention : forcé l'écriture en encodage utf-8
        with open('gpx//utagawavtt-{}.gpx'.format(id_track),'w',encoding="utf-8") as f :
            f.write(rep.text)
            print('Save file gpx//utagawavtt-{}.gpx'.format(id_track))
    else:
        # Afficher un message d'erreur si la requête a échoué
        print("La requête GET a échoué.")
        return None
        
def get_one_track_Tracegps(id_track):
    url = 'http://www.tracegps.com/index.php?func=telecharge&idcircuit={}&type=gpx'.format(id_track)
    rep = requests.get(url)
    with open('gpx//tracegps-{}.gpx'.format(id_track),'w', encoding="utf-8") as f :
        f.write(rep.text)
        print('Save file gpx//tracegps-{}.gpx'.format(id_track))
        
def get_idtrack(rep):
    idtracks = []
    soup = BeautifulSoup(rep.text)
    lst_a= soup.find_all('a', { 'class' : 'Style20'}, onclick=True)
    for a in lst_a:
        href = a['onclick']
        if 'parcours' in href:
            sp = href.split('circuit')
            if len(sp) == 2:
                sp = sp[1].split('.')
                if len(sp) == 2:
                    id_trace = sp[0]
                    idtracks.append(id_trace)
    return idtracks
        
def get_track_near_point_Tracegps(lon_min, lat_min, lon_max, lat_max):
    lst_idtrack = []
    grid_lon = np.arange(lon_min,lon_max,0.1)
    grid_lat = np.arange(lat_min,lat_max,0.1)
    for lon in grid_lon : 
        for lat in grid_lat : 
            print(f"Réponse tracegps avec lon = {lon} et lat = {lat}")
            url = f"http://www.tracegps.com/index.php?func=liste&code=coord&lat={lat}&lon={lon}"
            rep = requests.get(url)
            idtracks = get_idtrack(rep)
            print(f"les traces suivantes ont été détectées : {idtracks}")
            for t in idtracks : 
                if t is lst_idtrack :
                    print(f"trace {t} existe déjà")
                elif t not in lst_idtrack : 
                    lst_idtrack.append(t)
                    print(f"trace {t} ajoutée à la liste des traces")
    return lst_idtrack
        
def get_track_in_bbox_Camptocamp(E_min, N_min, E_max, N_max):
    url = 'https://api.camptocamp.org/outings?qa=draft,great&bbox={},{},{},{}offset=100&limit=100'.format(E_min, N_min, E_max, N_max)
    rep = requests.get(url)
    out = rep.json()
    print(url)
    for act in out['documents']:
        if act['geometry']['has_geom_detail']:
            docu_id = act['document_id']
            get_one_track_Camptocamp(docu_id)
    
def get_one_track_Camptocamp(doc_id): 
    GoogleMercatortoWGS84 = Transformer.from_crs(3857,4326)
    url = "https://api.camptocamp.org/outings/{}".format(doc_id)
    print(url)
    rep = requests.get(url)
    out = rep.json()
    geom = out['geometry']['geom_detail']
    geom_dict = eval(geom)
    typecoord = geom_dict['type']
    coordinates = geom_dict['coordinates']
    if typecoord == 'LineString':
        print(coordinates)
        new_coord = [list(GoogleMercatortoWGS84.transform(coord[0], coord[1])) for coord in coordinates]
        print(new_coord)
    elif typecoord == 'MultiLineString':
        for linestring in coordinates :
            new_coord = [list(GoogleMercatortoWGS84.transform(coord[0], coord[1])) for coord in linestring]
            print(new_coord)
    geom_dict['coordinates'] = new_coord
    with open('json//camptocamp-{}.geojson'.format(doc_id),'w') as f :
        f.write(str(geom_dict))
    # with open('json//camptocamp-{}.txt'.format(doc_id),'w') as f :
    #     f.write(rep.text)
    
            
def get_track_in_bbox_Oppenrunner(lat_min, lon_min, lat_max, lon_max):
    activite = 3
    lst_track = []
    #Activité 3 = VTT
    url = 'https://api.openrunner.com/api/v2/routes?activities=5B%5D=3&north_west_lat={}&north_west_lng={}&south_east_lat={}&south_east_lng={}'.format(lat_min, lon_min, lat_max, lon_max)
    rep = requests.get(url)
    out = rep.json()
    print(out)

# FONCTION POUR RENDU RASTER "HEAT MAP"

bbox_lon_min = 5.40
bbox_lat_min = 45.40
bbox_lon_max = 5.60
bbox_lat_max = 45.60


if __name__ == "__main__":
    
    #-----UTAGAWAVTT-----
    if options['utagawavtt']:
        
        '''
        Site : https://www.utagawavtt.com/search?city=&w=[-7.65747,41.50034,10.82154,51.35119]&q=[1,2,3,4]&k=0&l=all&u=1&aa=25
        Utilise requests (ajout d'un header nécessaire)
        Reponse de la requête : format json contenant la liste des traces disponibles (avec gestion multipage)
        A partir des identifiants de la liste des tracks : récupération de la réponse txt au format gpx
        --> gpx
        '''
        # res_utawaga = get_track_in_bbox_Utagawavtt(bbox_lon_min,bbox_lat_min,bbox_lon_max,bbox_lat_max)
        # for i,r in enumerate(res_utawaga) :
        #     get_one_track_Utagawavtt(r['tid'])
        
    #-----TRACE GPS-----
    if options['tracegps']:
        '''
        Site : https://www.utagawavtt.com/search?city=&w=[-7.65747,41.50034,10.82154,51.35119]&q=[1,2,3,4]&k=0&l=all&u=1&aa=25
        Utilise Beautifulsoup pour chercher les identifiants des traces directement dans la page html
        Ajouter la gestion des pages
        Pas de données en Suisse
        --> gpx
        '''
        # lst_idtracks = get_track_near_point_Tracegps(bbox_lon_min,bbox_lat_min,bbox_lon_max,bbox_lat_max)
        # for i in lst_idtracks : 
        #     get_one_track_Tracegps(i)
        
    #-----OPENSTREETMAP-----
    if options['openstreetmap']:
        '''
        Site : https://www.utagawavtt.com/search?city=&w=[-7.65747,41.50034,10.82154,51.35119]&q=[1,2,3,4]&k=0&l=all&u=1&aa=25
        Utilise l'api d'openstreet map
        --> gpkg
        '''
        # north, south, east, west
        gdf = ox.geometries.geometries_from_bbox(bbox_lat_max, bbox_lat_min, bbox_lon_min, bbox_lon_max, tags={'mtb:scale': True})
        gdf.plot()
    
        del gdf['nodes'] # car c'est une liste et que gpkg ne sait pas gérer les listes
        gdf.to_file('gpkg//dataframe.gpkg', driver='GPKG', layer='name')
    
    
    #-----CAMPTOCAMP----
    if options['camptocamp']:
        '''
        --> json
        '''
        #attention E_min, N_min, E_max, N_max en EPSG:3857 Google Maps Global Mercator
        WGS84toGoogleMercator = Transformer.from_crs(4326,3857)
        bbox_E_min, bbox_N_min = WGS84toGoogleMercator.transform(bbox_lat_min, bbox_lon_min)
        bbox_E_max, bbox_N_max = WGS84toGoogleMercator.transform(bbox_lat_max, bbox_lon_max)
        GoogleMercatortoWGS84 = Transformer.from_crs(3857,4326)
        # lat,lon = GoogleMercatortoWGS84.transform(bbox_E_max,bbox_N_min)
        get_track_in_bbox_Camptocamp(bbox_E_min,bbox_N_min,bbox_E_max,bbox_N_max)
        

    
    #-----OPENRUNNER----
    if options['openrunner']:
    
        get_track_in_bbox_Oppenrunner(bbox_lat_min,bbox_lon_min, bbox_lat_max, bbox_lon_max)
        polyline.decode('u{~vFvyys@fS]')
    
    
    #-----BIKINISPOT----
    
    # url = "https://www.bikingspots.ch/leaflet/searchForLeaflet.php?type=&area=&search=&deniv=&dist=&diff="
    # response = urlopen(url)
    # data = json.loads(response.read())
    # print(data['success'])
    # for tr in data['result']:
    #     file_name = os.path.join('bikingspots',tr['file'].replace('.xml','.gpx'))
    #     print(file_name)
    #     if not os.path.isfile(file_name):
    #         try:
    #             urlretrieve(url_gpx+tr['file'], file_name)
    


# ---- GPX ----
gpx_folder_path = 'gpx'
gpx_files = rz.get_file_names(gpx_folder_path)

# ---- GPKG ----
gpkg_file = "gpkg\\dataframe.gpkg"

# ---- GEOJSON ----
geojson_folder_path = 'json'
geojson_files = rz.get_file_names(geojson_folder_path)


# ---- Rasterize ----
rz.rasterize(gpx_files, gpkg_file, geojson_files,'raster_total_rasterio.tif')


# numpy_array = gdal_to_numpy(out_raster_ds)
# print(numpy_array.shape)