# -*- coding: utf-8 -*-
"""
Created on Wed May 24 13:13:37 2023

@author: Bruno
"""
from PIL import Image
import numpy as np


image = Image.open("image_low.png")
arr=np.asarray(image)



# CREATION D'UN RANDOM DE ARRAY
def random_array(size, scale):
        tuile_array = np.ones(shape=(size,size))
        for i in range(size):
            for j in range(size):
                tuile_array[i][j]=np.abs(np.round(np.random.normal(loc=0.0, scale=scale, size=None)))
        return tuile_array
    
    
tuile= random_array(256,150)

for i in range(256):
    for j in range(256):
        tuile[i][j]=int(arr[i][j][3]*80/256)


def generate_color_rgba_from_nbre(nb, fact, type_color):
    """
    

    Parameters
    ----------
    nb : int
        nombre à transformer en RGBA
    fact : int
        facteur pour rgb maximum et pas de transparence.
    type_color : string
        "r" : red / "g" = green / "b" : bleu / "w": white.

    Returns
    -------
    list
        [r,g,b,a]

    """
    # initialisation RGBA
    r=0
    g=0
    b=0
    a=0
    col_haut=255
    col_bas=0
    if type_color=="r" or type_color=="g" or type_color=="b":
        col_haut=100
        col_bas=255
    
    # Longeur de la couleur d'échelle
    l_col=abs(col_haut-col_bas)
    
    degre=2
    mult_c=l_col/(fact**degre)
    mult_deg=255/(fact**degre)
    mult_log=255/np.log2(fact+1)
    mult_lin=255/fact
    
    
    color=mult_c*nb**degre
    
    # transparence selon log
    # a=mult_log*np.log2(nb+1)
    
    # Transparence selon degré
    a=mult_deg*nb**degre
    
    # Transparence selon linéaire
    # a=mult_lin*nb
    
    if color>l_col:
        color=l_col
    if a>255:
        a=255
    
    if type_color=="r":
        r=col_bas-color
    elif type_color=="g":
        g=col_bas-color
    elif type_color=="b":
        b=col_bas-color
    else:
        r=color
        g=color
        b=color
    
    return [r,g,b,a]

def create_image_from_array(array, color):
    """
    

    Parameters
    ----------
    array : np.array
        array 256x256 contenant le nbre de passage.
    color : string
        "r" : red / "g" = green / "b" : bleu / "w": white

    Returns
    -------
    image_create : img
        image RGBA.
    color_image : array RGBA (256x256x4)
        valeur int des RGBA dans un array.

    """
    color_image = np.zeros(shape=(256,256,4), dtype="uint8")
    
    for i in range(array.shape[0]) :
        for j in range(array.shape[1]):
            color_rgba=generate_color_rgba_from_nbre(array[i][j],80, color)
            
            
            color_image[i][j][0]=color_rgba[0]
            color_image[i][j][1]=color_rgba[1]
            color_image[i][j][2]=color_rgba[2]
            color_image[i][j][3]=color_rgba[3]
            
            
    image_create = Image.fromarray(color_image)
    return image_create, color_image

im,array_img= create_image_from_array(tuile, 'r')
image.show()
im.show()