import cv2
import glob
from pytesseract import pytesseract
from remove_lines import remove_lines
from pdf2image import convert_from_path


def createROIs(path_to_pdf):
    texts = []
    images = convert_from_path(path_to_pdf)
    images[0].save("processImages/sample_document.jpg", "JPEG")

    for image_file in glob.glob(r"processImages/sample_document.jpg"):
        remove_lines(image_file, r"processImages/")

    # PREPROCESSING
    image = cv2.imread(r"processImages/sample_document.jpg")
    base_image = image.copy()
    # GRAYSCALE
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # BLUR
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    # THRESHOLD
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # KERNEL SIZE
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (75, 45))
    # DILATING
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    # FINDING CONTOURS
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda z: cv2.boundingRect(z)[0])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 100:
            roi = base_image[y: y + h, x: x + w]
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 5)
            ocr = pytesseract.image_to_string(roi)
            ocr = "".join(
                [s for s in ocr.strip().splitlines(True) if s.strip()])
            texts.append(ocr)
    cv2.imwrite("processImages/sample_document_Bbox.png", image)
    return texts
