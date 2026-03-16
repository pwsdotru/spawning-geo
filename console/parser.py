from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re
import json

stats ={"total": 0, "error": 0, "error_parse": [], "error_convert": [], "empty_points": []}

#1. 55°43'00,7" с.ш. 54°16'41,0" в.д.
def parse_coords(input):
    res = {"lng": "0.0", "lat": "0.0"}
    stats["total"] += 1
    pos = re.search(r"\d+\.", input)
    if (pos):
        coords = input[pos.end(0):]
        sep = re.search(r"ш\.?", coords)
        if sep:
            res["lng"] = coords[:sep.end(0)].strip(', "')
            res["lat"] = coords[sep.end(0):].strip(', "')
            return res
    stats["error"] += 1
    stats["error_parse"].append(input)
    return None 

def convert_coords(input):
    params = {
        "degrees":{"value": 0, "separator": '°', "isint": True},
        "minutes":{"value": 0, "separator": '\'', "isint": True},
        "seconds":{"value": 0.0, "separator": '"', "isint": False}
    }

    res = 0.0
    save_input = input
    sign = 1
    degrees = 0
    minutes = 0
    seconds = 0

    if input == "0.0":
        return None

    if re.match(r"ю\.?", input) or re.match(r"з\.?", input):
        sign = -1

    for k in params:
        sep = re.search(params[k]["separator"], input)
        if sep:
            value = input[:sep.end() - 1]
            input = input[sep.end():]
            if params[k]["isint"]:
                data = value.strip()
                if re.match(r"^\d+$", data):
                    params[k]["value"] = int(data)
                else:
                    stats["error"] += 1
                    stats["error_convert"].append(save_input + " [" + data + "]")
                    return None
            else:
                data = value.strip().replace(",", ".").replace(" ", ".")
                if re.match(r"^\d+(\.\d+)?$", data):
                    params[k]["value"] = float(data)
                else:
                    stats["error"] += 1
                    stats["error_convert"].append(save_input + " [" + data + "]")
                    return None

    res = params["degrees"]["value"] + params["minutes"]["value"]/60.0 + params["seconds"]["value"]/3600.0
    return res*sign

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
        region = ""
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
                    point = parse_coords(p.text)
                    if point != None:
                        point["lng_geo"] = convert_coords(point["lng"])
                        point["lat_geo"] = convert_coords(point["lat"])
                    geo_data[region_count]["data"][data_count]["points"].append(point)
                else:
                    if geo_data[region_count]["data"][data_count]["title"] != "":
                        geo_data[region_count]["data"][data_count]["title"] += " "
                    geo_data[region_count]["data"][data_count]["title"] = geo_data[region_count]["data"][data_count]["title"] + p.text
        data_count = data_count + 1


output_json = []
for rid, region in geo_data.items():
#    print(region)
    collection = {"type":"FeatureCollection", "features":[]}
    for pid, data in region["data"].items():
        coords = []
        if len(data["points"]) > 0:
            for point in data["points"]:
                coords.append([point["lat_geo"], point["lng_geo"]])

            feature = {
                "type":"Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates":[coords]
                },
                "properties": {
                    "description": region["region"] + " -> " + data["title"]
                }
            }
            collection["features"].append(feature)
        else:
            stats["error"] += 1
            stats["empty_points"].append(data["title"])
    output_json.append(collection)
    print(json.dumps(output_json, indent=4))
    exit()
