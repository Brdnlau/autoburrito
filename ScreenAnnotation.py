from textwrap import wrap
import numpy as np
import cv2 as cv
from PIL import ImageGrab
import os
import time
from pynput.keyboard import Key, Controller
import keyboard
import autoit
import pytesseract

# initialize
REFERENCES = {}
THRESHOLD = 0.1
customerOrder = ""
burrcnt=0

kb = Controller()
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

for file in os.listdir(os.fsencode('FoodPics/')):  
    REFERENCES[os.fsdecode(file)[:-4]] = [cv.cvtColor(cv.imread('FoodPics/' + os.fsdecode(file)),cv.COLOR_RGB2HSV), 0, 0]
    REFERENCES[os.fsdecode(file)[:-4]] = [cv.cvtColor(cv.imread('FoodPics/' + os.fsdecode(file)),cv.COLOR_RGB2HSV), 0, 0]

with open('Coords.txt') as f:
    lines = f.readlines()
for line in lines:
    text = line.split(' ')
    REFERENCES[text[0]][1] = text[1]
    REFERENCES[text[0]][2] = text[2][:-1]

def calculate_similarity(img, templ):
    result = cv.matchTemplate(img, templ, cv.TM_SQDIFF_NORMED)
    min_val = cv.minMaxLoc(result)[0]
    return min_val

def roll_burrito():
    kb.press(Key.left) # Presses "left" key
    kb.release(Key.left)
    time.sleep(0)
    kb.press(Key.right)
    kb.release(Key.right)
    time.sleep(0)
    kb.press(Key.up) # Presses "up" key
    kb.release(Key.up)

def drag_drop_ingredient():
    #jump mouse to correct ingredient and drag it to burrito location
    autoit.mouse_move(960, 650,2)
    dropframe = cv.cvtColor(np.array(ImageGrab.grab(bbox=(30, 810, 1920, 811))), cv.COLOR_BGR2GRAY)#x1, y1, x2, y2 https://www.codegrepper.com/code-examples/python/python+cv2+screen+capture
    for x in range(len(dropframe[0])):
        burritoX = 600
        if dropframe[0][x]>=235:
            burritoX = int(x*0.87)+340
            break
    #autoit.mouse_move(int(REFERENCES[customerOrder][1]), int(REFERENCES[customerOrder][2]),5)
    autoit.mouse_click_drag(int(REFERENCES[customerOrder][1]), int(REFERENCES[customerOrder][2]),burritoX,830,button="left", speed=2)

while True:
    # user interrupt
    if keyboard.is_pressed("q"):
        exit()
    
    #move mouse to 1920/2 x 400ish
    autoit.mouse_move(960, 650,2)

    #screen capture top of screen
    pickframe = cv.cvtColor(np.array(ImageGrab.grab(bbox=(500, 65, 1920-750, 235))), cv.COLOR_BGR2HSV)#x1, y1, x2, y2 https://www.codegrepper.com/code-examples/python/python+cv2+screen+capture
    
    #determine what is most likely the image shown on screen
    bestMatch = (1, "xd")
    for topping in REFERENCES.keys():
        if (calculate_similarity(pickframe,REFERENCES[topping][0]) < bestMatch[0]):
            bestMatch = (calculate_similarity(pickframe,REFERENCES[topping][0]), topping)
    if bestMatch[0] < THRESHOLD:
        customerOrder = bestMatch[1]
        #if burito stage then wrap burrito and repeat first 2 steps but slower
        if (customerOrder == "wrap"):
            roll_burrito()
            burrcnt+=1
            print(burrcnt)
            time.sleep(1)
            # check burritos rolled via image detection
            '''BurritoNumberframe = ImageGrab.grab(bbox=(1766, 87, 1813, 107))#x1, y1, x2, y2
            burritosWrapped =  pytesseract.image_to_string(BurritoNumberframe, config='--psm 6')
            print(burritosWrapped)
            #burritosWrapped = ''.join(x for x in burritosWrapped if x.isdigit())
            #if burritosWrapped != "":
                #print(int(burritosWrapped))
            if burritosWrapped == '2.4K':
                exit()
            time.sleep(0.2)'''
            # check burritos rolled via counter
        elif (customerOrder == "blank"):
            roll_burrito()
            for topping in REFERENCES.keys():
                customerOrder = topping
                drag_drop_ingredient()
            roll_burrito()
        elif (customerOrder == "fuzzy"):
            roll_burrito()
        else:
            drag_drop_ingredient()