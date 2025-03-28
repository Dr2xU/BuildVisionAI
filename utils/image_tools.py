import cv2
import numpy as np
import pytesseract
from pytesseract import Output

def preprocess_image(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    _, binary_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    lower_color = np.array([0, 30, 30])
    upper_color = np.array([180, 255, 255])
    color_mask = cv2.inRange(hsv, lower_color, upper_color)
    edges = cv2.Canny(gray, 50, 150)

    combined_mask = cv2.bitwise_or(binary_thresh, color_mask)
    combined_mask = cv2.bitwise_or(combined_mask, edges)

    kernel = np.ones((3, 3), np.uint8)
    cleaned_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    return cleaned_mask

def detect_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    config = r'--oem 3 --psm 11'
    ocr_result = pytesseract.image_to_data(thresh, lang=None, config=config, output_type=Output.DICT)

    text_data = []
    for i in range(len(ocr_result['text'])):
        text = ocr_result['text'][i].strip()
        conf = int(ocr_result['conf'][i])
        if text and conf > 30 and len(text) > 0:
            x, y, w, h = (
                ocr_result['left'][i],
                ocr_result['top'][i],
                ocr_result['width'][i],
                ocr_result['height'][i]
            )
            text_data.append({
                "text": text,
                "confidence": conf,
                "bounding_box": (x, y, x + w, y + h)
            })

    text_data.sort(key=lambda item: (item["bounding_box"][1] // 10, item["bounding_box"][0]))
    return text_data

def detect_symbols(image, min_area=50, max_area=None, visualize=False):
    mask = preprocess_image(image)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if min_area < area and (max_area is None or area < max_area):
            boxes.append((x, y, x + w, y + h))

    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))

    merged_boxes = []
    for box in boxes:
        added = False
        for i in range(len(merged_boxes)):
            x1, y1, x2, y2 = merged_boxes[i]
            bx1, by1, bx2, by2 = box
            if abs(y1 - by1) < 20 and abs(x1 - bx1) < 20:
                nx1, ny1 = min(x1, bx1), min(y1, by1)
                nx2, ny2 = max(x2, bx2), max(y2, by2)
                merged_boxes[i] = (nx1, ny1, nx2, ny2)
                added = True
                break
        if not added:
            merged_boxes.append(box)

    symbol_data = []
    for i, (x1, y1, x2, y2) in enumerate(merged_boxes):
        roi = image[y1:y2, x1:x2]
        text_results = detect_text(roi)
        for t in text_results:
            t['relative_bounding_box'] = (
                x1 + t['bounding_box'][0],
                y1 + t['bounding_box'][1],
                x1 + t['bounding_box'][2],
                y1 + t['bounding_box'][3]
            )

        symbol = {
            "Symbol_ID": i + 1,
            "X": x1,
            "Y": y1,
            "Width": x2 - x1,
            "Height": y2 - y1,
            "BoundingBox": (x1, y1, x2, y2),
            "Text": text_results
        }
        symbol_data.append(symbol)

    if visualize:
        for symbol in symbol_data:
            x1, y1, x2, y2 = symbol['BoundingBox']
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            for text_info in symbol['Text']:
                tx1, ty1, tx2, ty2 = text_info['relative_bounding_box']
                cv2.rectangle(image, (tx1, ty1), (tx2, ty2), (255, 0, 0), 1)

    return image, symbol_data
