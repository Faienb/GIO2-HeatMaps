# -*- coding: utf-8 -*-
"""
Created on Wed May 24 13:13:37 2023

@author: Bruno
"""
from PIL import Image
import numpy as np


image = Image.open("image_exemple.jpg")
arr=np.asarray(image)

# CREATION D'UN RANDOM DE ARRAY
def random_array(size, scale):
        tuile_array = np.ones(shape=(size,size))
        for i in range(size):
            for j in range(size):
                tuile_array[i][j]=np.abs(np.round(np.random.normal(loc=0.0, scale=scale, size=None)))
        return tuile_array
    
    
tuile= random_array(256,150)


def facteur_color(nb, fact):
    mult=5
    a=(255-mult*fact**2)/fact
    
    
    color=mult*nb**2+a*nb
    if color>255:
        color=255
    
    return color
    
def create_image_from_chaleur(array):
    color_image = np.zeros(shape=(256,256,3), dtype="uint8")
    
    for i in range(array.shape[0]) :
        for j in range(array.shape[1]):
            color_rgb=facteur_color(array[i][j],350)
            color_image[i][j][0]=color_rgb
            color_image[i][j][1]=color_rgb
            color_image[i][j][2]=color_rgb
    image_create = Image.fromarray(color_image)
    return image_create, color_image

im,array_img= create_image_from_chaleur(tuile)
im.show()