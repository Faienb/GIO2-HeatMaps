import numpy as np

def fusion_tuile_bruno(json_recv):
    element_send = {
        "Z" : json_recv['Z'],
        "X" : json_recv['X'],
        "Y": json_recv['Y'],
        "status" : json_recv['status'],
        "completion" : json_recv['completion'],
        "task" : json_recv['task'],
        "tuile_array" : [
            ]
    }
    
    ar1=np.concatenate((json_recv['tuile_array1'], json_recv['tuile_array2']), axis=1)
    ar2=np.concatenate((json_recv['tuile_array3'], json_recv['tuile_array4']), axis=1)
    array_fus=np.concatenate((ar1, ar2), axis=0)
    
    
    array_reduced=np.zeros(shape=(256,256))
    
    # Création d'une somme de array
    for i in range(256):
        for j in range(256):
            x1y1=array_fus[j+j,i+i]
            x2y1=array_fus[j+j,i+i+1]
            x1y2=array_fus[j+j+1,i+i]
            x2y2=array_fus[j+j+1,i+i+1]
            array_reduced[j,i]=x1y1+x2y1+x2y2+x1y2

    # Enregistrement du array dans le dictionnaire de livraison
    element_send["tuile_array"]=array_reduced
    
    return array_reduced