import cv2
import numpy as np
from matplotlib import pyplot as plt

def myCanny(image, threshold1, threshold2):
    # filter image with Gaussian
    gauss = cv2.GaussianBlur(image,(5,5),0)
    gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)

    # start with a Sobel filter?
    scharrX = cv2.Scharr(gray, -1, 1, 0)
    scharrY = cv2.Scharr(gray, -1, 0, 1)

    # cv2.imshow("Sobel in X", sobX)
    # cv2.imshow("Sobel in Y", sobY)
    # use to compute magnitude, direction at every point
    # print(len(sobX[:, 0]))

    #grad_2 = np.zeros((len(sobX[:, 0]), len(sobX[0, :])), dtype=tuple)

    #grad_2 = scharrX
    
    
    


img = cv2.imread('../../180D_WarmUp/Flag-USA.jpg', cv2.IMREAD_COLOR)
img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#print(img2)

#myCanny(img, 10, -1)
#gauss = cv2.GaussianBlur(img,(5,5),0)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# start with a Sobel filter?
scharrX = cv2.Scharr(img, -1, 1, 0)
scharrY = cv2.Scharr(img, -1, 0, 1)
laplacian = cv2.Laplacian(gray, cv2.CV_64F)
print(scharrX)

"""
for i in range(len(scharrX[:,0])):
    for j in range(len(scharrX[0, :])):
        if((scharrX[i,j] < 255) and (scharrX[i,j] > 0)):
            print("Middle")
            break
"""

while(1):
    
    cv2.imshow('og',img)
    cv2.imshow("Sobel in X", scharrX)
    cv2.imshow("Sobel in Y", scharrY)
    cv2.imshow("Laplacian", laplacian)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
