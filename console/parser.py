from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re

stats ={"total": 0, "error": 0, "incorrect": []}

#1. 55°43'00,7" с.ш. 54°16'41,0" в.д.
def parse_coords(input):
    res = {"lng": 0.0, "lat": 0.0}
    stats["total"] += 1
#    print(input)
    coords_pattern = "\\d{1,3}\\.\\s+(\\d{1,3})°(\\d{1,3})'(\\d{1,3})[\\,\\s]?(\\d{1,6})?\\\"?\\s+([с|ю]{1}\\.ш\\.)[\\s\\,]+(\\d{1,3})°(\\d{1,3})'(\\d{1,3})[\\,\\s]?(\\d{1,6})?\\\"?\\s+([в|з]{1}\\.д\\.)";
    data = re.match(coords_pattern, input, re.IGNORECASE)
    if data:
#       print(data)
        res["lng"] = data
        res["lat"] = data
    else:
        stats["error"] += 1
        stats["incorrect"].append(input)
#    print(res)
#    exit()
    return res


ns = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    }
geo_data = {}
region_count = -1
data_count = 0

regexp = re.compile("[0-9]{1,3}\\.")

path = "doc.odt"
with ZipFile(path) as z, z.open("content.xml") as f:
    root = ET.parse(f).getroot()


for cell in root.findall(f".//table:table-cell", ns):
    headers = cell.findall(f".//text:h", ns)
    if len(headers) > 0:
        region = "";
        for h in headers:
            if None != h.text:
                region = region + h.text
        region_count = region_count + 1
        geo_data[region_count] = {"region": region, "data": {}}
        data_count = 0

    paragraphs = cell.findall(f".//text:p", ns)
    if region_count >= 0 and len(paragraphs) > 2:
        geo_data[region_count]["data"][data_count] = {"title": "", "points": []}
        for p in paragraphs:
            if None != p.text:
                if regexp.match(p.text):
                    geo_data[region_count]["data"][data_count]["points"].append(parse_coords(p.text))
                else:
                    if geo_data[region_count]["data"][data_count]["title"] != "":
                        geo_data[region_count]["data"][data_count]["title"] += " "
                    geo_data[region_count]["data"][data_count]["title"] = geo_data[region_count]["data"][data_count]["title"] + p.text
        data_count = data_count + 1

#print(geo_data)
print(stats)
