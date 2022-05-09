import numpy as np
import imutils
import cv2
import os
import argparse
import json

filename = "/home/nos/00801_locB_2008_spring_0083.jpg"
f = open("/home/nos/cutout/locB_2010_spring_0230_0174.json")
data = json.load(f)
box = np.array(data[0]["bbox"])
mask = np.array(data[0]["segmentation"][0])

image = cv2.imread(filename)
image = imutils.resize(image, width=600)
cv2.imshow("Input",image)

#cv2.waitKey(0)


(startX, startY, endX, endY) = box
boxW = endX
boxH = endY
print(mask)
mask = cv2.resize(mask, (boxW, boxH),
interpolation=cv2.INTER_CUBIC)
mask = (mask > args["threshold"]).astype("uint8") * 255
# allocate a memory for our output Mask R-CNN mask and store
# the predicted Mask R-CNN mask in the GrabCut mask
rcnnMask = np.zeros(image.shape[:2], dtype="uint8")
rcnnMask[startY:endY, startX:endX] = mask
# apply a bitwise AND to the input image to show the output
# of applying the Mask R-CNN mask to the image
rcnnOutput = cv2.bitwise_and(image, image, mask=rcnnMask)
# show the output of the Mask R-CNN and bitwise AND operation
cv2.imshow("R-CNN Mask", rcnnMask)
cv2.imshow("R-CNN Output", rcnnOutput)
