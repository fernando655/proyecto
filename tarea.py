import numpy as np
import cv2 
import os
imagen= cv2.imread(os.path.dirname(__file__)+'\\win2.jpg')
imagen= cv2.resize(imagen,(300,300))

ktam=(5,5)
sigma=200.5
gausiano=cv2.GaussianBlur(imagen,ktam,sigma)

#array_imagen = np.array(imagen)
#array_resultado = (255 - array_imagen)-3
#imagen_resultado = np.array(array_resultado, dtype=np.uint8)
cv2.imshow('Imagen Original', imagen)
cv2.imshow('Imagen Resultante', gausiano)
cv2.waitKey(0)
cv2.destroyWindow()