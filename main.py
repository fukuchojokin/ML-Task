import glob
import json
import re

import cv2
from pdf2image import convert_from_path
from pytesseract import pytesseract

from remove_lines import remove_lines

images = convert_from_path(r'Sample.pdf')
images[0].save("processImages/BOL.jpg", "JPEG")

for jpg_file in glob.glob(r'processImages/BOL.jpg'):
    remove_lines(jpg_file, r'processImages/')

## PREPROCESSING
image = cv2.imread(r"processImages/BOL.jpg")
base_image = image.copy()
# GRAY
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite("processImages/BOL_gray.png", gray)
# BLUR
blur = cv2.GaussianBlur(gray, (7, 7), 0)
cv2.imwrite("processImages/BOL_blur.png", blur)
# THRESH
thresh = cv2.threshold(
    blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
)[1]
cv2.imwrite("processImages/BOL_thresh.png", thresh)
# KERNEL
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (75, 45))
cv2.imwrite("processImages/BOL_kernel.png", kernel)
# DILATE
dilate = cv2.dilate(thresh, kernel, iterations=1)
cv2.imwrite("processImages/BOL_dilate.png", dilate)
# CONTOURS
cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
cnts = sorted(cnts, key=lambda z: cv2.boundingRect(z)[0])

regex = {
    "seller": re.compile(r"Seller.*\n([\s\S]+)"),
    "buyer": re.compile(r"Buyer.*\n([\s\S]+)"),
    "container": re.compile(r"[A-Z]{4}[0-9]{7}"),
    "pol": re.compile(r"POL *\n([A-Za-z, ]+)"),
    "pod": re.compile(r"POD *\n([A-Za-z, ]+)"),
    "eta": re.compile(r"ETA.*(\d{4}(?:\/\d{2}){2})"),
    "etd": re.compile(r"ETD.*(\d{4}(?:\/\d{2}){2})"),
    "vessel_name": re.compile(r"Vessel *\/ *Voyage *\n([A-Z ]+)"),
    "voyage_num": re.compile(r"\b([A-Z0-9]{5})\b *\n*ETA of POD"),
    "mbl_num": re.compile(r"[A-Z0-9]{9} *([A-Z0-9]{9})"),
    "mbl_scac": re.compile(r"SCAC.*\n[A-Z]{4} ([A-Z]{4})"),
    "hbl_num": re.compile(r"([A-Z0-9]{9}) *[A-Z0-9]{9}"),
    "hbl_scac": re.compile(r"SCAC.*\n([A-Z]{4}) [A-Z]{4}"),
    "type_of_movement": re.compile(r"(FCL *[A-Za-z]+|LCL *[A-Za-z]+)"),
}
texts = []
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    if h > 100:
        roi = base_image[y:y + h, x:x + w]
        cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 5)
        ocr = pytesseract.image_to_string(roi)
        ocr = "".join([s for s in ocr.strip().splitlines(True) if s.strip()])
        texts.append(ocr)
        
cv2.imwrite("processImages/BOL_Bbox.png", image)

output = {}
for text in texts:
    for key in regex:
        match = re.findall(regex[key], text)
        if len(match) > 0:
            output[key] = str(match.pop()).replace("\n", " ")
            output[key] = re.sub('[^A-Za-z0-9.,\n ]', '', output[key])
            if re.search(r'LCL.*', output[key]):
                output[key] = re.sub('LCL.*', 'LCL', output[key])
            elif re.search(r'FCL.*', output[key]):
                output[key] = re.sub('FCL.*', 'FCL', output[key])

output = [output]
with open('extraction.json', 'w') as f:
    json = json.dumps(output, indent=4, sort_keys=True)
    f.write(json)
    print(json)
