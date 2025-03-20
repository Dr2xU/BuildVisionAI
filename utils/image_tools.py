import cv2
import numpy as np

def detect_symbols(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    lower_bound = np.array([0, 30, 30])
    upper_bound = np.array([180, 255, 255])
    color_mask = cv2.inRange(hsv, lower_bound, upper_bound)

    _, black_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    combined_mask = cv2.bitwise_or(color_mask, black_mask)

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    symbol_data = []
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500:
            symbol_data.append({"Symbol_ID": i + 1, "X": x, "Y": y, "Width": w, "Height": h})

    return image, symbol_data
