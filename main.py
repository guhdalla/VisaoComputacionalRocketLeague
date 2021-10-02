import time
import cv2
import os, sys, os.path
import numpy as np
import math
import pyautogui
import pynput
from pynput.keyboard import Key, Controller

# verde
greenLower = (52, 86, 6)
greenUpper = (87, 255, 255)

# amarelo
yellowLower = (24, 55, 55)
yellowUpper = (50, 255, 255)


def filtro_de_cor(img_bgr, low_hsv, high_hsv):
    """ retorna a imagem filtrada"""
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, low_hsv, high_hsv)
    return mask


def mascara_or(mask1, mask2):
    """ retorna a mascara or"""
    mask = cv2.bitwise_or(mask1, mask2)
    return mask


def mascara_and(mask1, mask2):
    """ retorna a mascara and"""
    mask = cv2.bitwise_and(mask1, mask2)

    return mask


def desenha_cruz(img, cX, cY, size, color):
    """ faz a cruz no ponto cx cy"""
    cv2.line(img, (cX - size, cY), (cX + size, cY), color, 5)
    cv2.line(img, (cX, cY - size), (cX, cY + size), color, 5)


def escreve_texto(img, text, origem, color):
    """ faz a cruz no ponto cx cy"""

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, str(text), origem, font, 0.4, color, 1, cv2.LINE_AA)


def controls(angle, area):
    keys = [
        pynput.keyboard.KeyCode.from_char('w'),
        pynput.keyboard.KeyCode.from_char('s'),
        pynput.keyboard.KeyCode.from_char('a'),
        pynput.keyboard.KeyCode.from_char('d'),
    ]
    keyboard = Controller()
    if angle > 270 and angle < 340:
        keyboard.press(keys[3])
        time.sleep(0.1)
        keyboard.release(keys[3])
    if angle < 90 and angle > 20:
        keyboard.press(keys[2])
        time.sleep(0.1)
        keyboard.release(keys[2])
    if area > 5500:
        keyboard.press(keys[0])
        time.sleep(0.1)
        keyboard.release(keys[0])
    if area < 3500 and angle > 0:
        keyboard.press(keys[1])
        time.sleep(0.1)
        keyboard.release(keys[1])


def image_da_webcam(img):
    contornos_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    maskGreen = cv2.inRange(contornos_img, greenLower, greenUpper)
    maskGreen = cv2.erode(maskGreen, None, iterations=2)
    maskGreen = cv2.dilate(maskGreen, None, iterations=2)

    maskYellow = cv2.inRange(contornos_img, yellowLower, yellowUpper)
    maskYellow = cv2.erode(maskYellow, None, iterations=2)
    maskYellow = cv2.dilate(maskYellow, None, iterations=2)

    # Encontrar contornos da mascara e inicializar a corrente
    cntGreen = cv2.findContours(maskGreen.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    centerGreen = None
    cntYellow = cv2.findContours(maskYellow.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    centerYellow = None

    # Unica proceder se pelo menos um contorno foi encontrado
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    area1 = 0
    area2 = 0
    if len(cntGreen) > 0:
        cGreen = max(cntGreen, key=cv2.contourArea)
        MGreen = cv2.moments(cGreen)
        if MGreen["m00"] != 0:
            x1 = int(MGreen["m10"] / MGreen["m00"])
            y1 = int(MGreen["m01"] / MGreen["m00"])
        rectGreen = cv2.minAreaRect(cGreen)
        boxGreen = cv2.boxPoints(rectGreen)
        boxGreen = np.int0(boxGreen)
        centerGreen = (x1, y1)
        cv2.drawContours(contornos_img, [boxGreen], 0, (0, 255, 0), 2)
        desenha_cruz(contornos_img, x1, y1, 20, (0, 255, 0))
        area1 = cv2.contourArea(cGreen)
        texto = "Centro: ", y1, x1, " Area: ", area1
        origem = (0, 25)
        escreve_texto(contornos_img, texto, origem, (0, 255, 0))

    if len(cntYellow) > 0:
        cYellow = max(cntYellow, key=cv2.contourArea)
        MYellow = cv2.moments(cYellow)
        if MYellow["m00"] != 0:
            x2 = int(MYellow["m10"] / MYellow["m00"])
            y2 = int(MYellow["m01"] / MYellow["m00"])
        rectYellow = cv2.minAreaRect(cYellow)
        boxYellow = cv2.boxPoints(rectYellow)
        boxYellow = np.int0(boxYellow)
        centerYellow = (x2, y2)
        cv2.drawContours(contornos_img, [boxYellow], 0, (0, 255, 255), 2)
        desenha_cruz(contornos_img, x2, y2, 20, (0, 255, 255))
        area2 = cv2.contourArea(cYellow)
        texto = "Centro: ", y2, x2, " Area: ", area2
        origem = (0, 50)
        escreve_texto(contornos_img, texto, origem, (0, 255, 255))

    color = (255, 255, 255)
    cv2.line(contornos_img, (x1, y1), (x2, y2), color, 5)

    vY = y1 - y2
    vX = x1 - x2
    rad = math.atan2(vY, vX)
    angle = math.degrees(rad)
    if angle < 0:
        angle += 360

    mediaArea = (area1 + area2) / 2
    controls(angle, mediaArea)
    texto = "Angle: ", angle
    origem = (0, 100)
    escreve_texto(contornos_img, texto, origem, (0, 255, 255))
    contornos_img2 = cv2.cvtColor(contornos_img, cv2.COLOR_HSV2BGR)
    return contornos_img2


cv2.namedWindow("preview")
# define a entrada de video para webcam
vc = cv2.VideoCapture(0)

# vc = cv2.VideoCapture("video.mp4") # para ler um video mp4

# configura o tamanho da janela
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if vc.isOpened():  # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:

    img = image_da_webcam(frame)  # passa o frame para a função imagem_da_webcam e recebe em img imagem tratada

    cv2.imshow("preview", img)
    # cv2.imshow("original", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
