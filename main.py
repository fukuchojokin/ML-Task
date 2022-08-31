import json
import re
import sys
from createROIs import createROIs

regex = {
    "buyer": re.compile(r"Buyer.*\n([\s\S]+)"),
    "container": re.compile(r"[A-Z]{4}[0-9]{7}"),
    "eta": re.compile(r"ETA of POD.*\n*(\d{4}(?:\/\d{2}){2})"),
    "etd": re.compile(r"ETD of POL.*\n*(\d{4}(?:/\d{1,2}){2})"),
    "hbl_num": re.compile(r"([A-Z0-9]{9}) *[A-Z0-9]{9}"),
    "hbl_scac": re.compile(r"SCAC.*\n([A-Z]{4}) [A-Z]{4}"),
    "mbl_num": re.compile(r"[A-Z0-9]{9} *([A-Z0-9]{9})"),
    "mbl_scac": re.compile(r"SCAC.*\n[A-Z]{4} ([A-Z]{4})"),
    "seller": re.compile(r"Seller.*\n([\s\S]+)"),
    "pod": re.compile(r"POD *\n([A-Za-z, ]+)"),
    "pol": re.compile(r"POL *\n([A-Za-z, ]+)"),
    "type_of_movement": re.compile(r"(FCL *[A-Za-z]+|LCL *[A-Za-z]+)"),
    "vessel_name": re.compile(r"Vessel *\/ *Voyage *\n([A-Z ]+)"),
    "voyage_num": re.compile(r"\b([A-Z0-9]{5})\b *\n*ETA of POD"),
}

try:
    file_path = sys.argv[1].replace('"', '')
    texts = createROIs(file_path)
except IndexError:
    file_path = input("Enter path to pdf file: ")
    texts = createROIs(file_path)

output = {}

for text in texts:
    for key in regex:
        match = re.findall(regex[key], text)
        if len(match) > 0:
            output[key] = str(match.pop()).replace("\n", " ")
            output[key] = re.sub("[^A-Za-z0-9.,/\n ]", "", output[key])
            if re.search(r"(LCL *[A-Za-z]+)", output[key]):
                output[key] = re.sub("(FCL *[A-Za-z]+)", "LCL", output[key])
            elif re.search(r"(FCL *[A-Za-z]+)", output[key]):
                output[key] = re.sub("(FCL *[A-Za-z]+)", "FCL", output[key])

with open("extraction.json", "w") as f:
    json = json.dumps([output], indent=4, sort_keys=True)
    f.write(json)
    print(json)