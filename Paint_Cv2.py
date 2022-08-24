import cv2
from cvzone.HandTrackingModule import HandDetector

import pygame
pygame.init()

w, h = 500, 500

red = (0, 0, 255)
green = (0, 255, 0)
black = (0, 0, 0)  # Instantiate colors
white = (255, 255, 255)
orange = (0, 165, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
indigo = (130, 0, 75)

colors = [red, orange, yellow, green, blue, indigo, black, white]

cap = cv2.VideoCapture(0)
cap.set(3, w)
cap.set(4, h)
detector = HandDetector()


class Circle:
    def __init__(self, cursor, color, size):
        self.center = cursor
        self.color = color
        self.size = size


class ColorBox:
    def __init__(self, before, after, color):
        self.before = before
        self.after = after
        self.color = color

        cv2.rectangle(img, (self.before[0], self.before[1]), (self.after[0], self.after[1]), self.color, cv2.FILLED)


class SizeCircle:
    def __init__(self, cursor, color):
        self.center = self.x, self.y = cursor
        self.color = color
        self.x1, self.x2 = self.center[0] -10, self.center[0] + 10
        self.y1, self.y2 = self.center[1] - 10, self.center[1] + 10


tuner = SizeCircle([w//5, (w//5) * 4], pygame.Color("gray"))  # create volume adjuster circle object to draw later

size = 10
currentcolor = black
circlelist = []

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)


    img = detector.findHands(img)
    lmList, _ = detector.findPosition(img)

    # Make the palette
    colorboxes = [ColorBox((i * w//8, 0), ((i * w//8) + w//8, w//8), colors[i]) for i in range(8)]

    # Make the container for the tuner / size adjuster
    whitebox = cv2.rectangle(img, (0, w//8), ((w//5) * 2, h), white, cv2.FILLED)


    cbefore, cafter = ((w//5) * 5, (w//5) * 3), ((w//5) * 5 + (w//8), (w//5) * 3 + (w//8))

    # Make the box that clears the canvas
    clearrect = ColorBox(cbefore, cafter, white)

    if lmList:
        l, _, _ = detector.findDistance(8, 12, img)

        if l < 30:
            cursor = lmList[8]

            if tuner.center[0] - 50 < cursor[0] < tuner.center[0] + 50 and 200 < cursor[1] < 600:
                tuner.y = cursor[1]  # change position of tuner on y axis
                size = int((600 - tuner.y) * 0.1)  # change size
                print(size)

            # If cursor collides with the eraser, delete all drawn circles on the canvas
            elif clearrect.before[0] < cursor[0] < clearrect.after[0] and clearrect.before[1] < cursor[1] < clearrect.after[1]:
                circlelist.clear()  # remove all circles from list to clear canvas
                currentcolor = white

            # If cursor collides with the palette, change the current color
            elif colorboxes[0].before[0] < cursor[0] < colorboxes[-1].after[0] and colorboxes[0].before[1] < cursor[1] < colorboxes[-1].after[1]:
                for box in colorboxes:
                    if box.before[0] < cursor[0] < box.after[0] and box.before[1] < cursor[1] < box.after[1]:
                        currentcolor = box.color

            # If cursor is in the canvas, draw circle
            elif 250 < cursor[0] and cursor[1] < 800:
                circlelist.append(Circle(cursor, currentcolor, size))

    # Draw the triangle
    cv2.line(img, (50, w//5 + w//8), (150, w//5 + w//8), red)
    cv2.line(img, (50, w//5 + w//8), (tuner.center[0], (w//5) * 4), red)
    cv2.line(img, (150, w//5 + w//8), (tuner.center[0], (w//5) * 4), red)

    # Draw tuner/volume adjuster
    cv2.circle(img, (tuner.x, tuner.y), 25, tuner.color, cv2.FILLED)

    for circle in circlelist:  # draw circles
        cv2.circle(img, circle.center, circle.size, circle.color, cv2.FILLED)

    cv2.imshow("Paint", img)

    cv2.waitKey(1)

    if cv2.getWindowProperty('Paint', cv2.WND_PROP_VISIBLE) < 1:
        break

