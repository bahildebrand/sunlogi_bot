import requests
import json
import math

ROOT_URL = "https://war-service-live.foxholeservices.com/api"

ICON_MAP = {
    33: "Storage Facility",
    45: "Relic Base",
    46: "Relic Base",
    47: "Relic Base",
    52: "Seaport",
    56: "Town Base",
    57: "Town Base",
    58: "Town Base",
}


def getMaps():
    MAPS_URL = ROOT_URL + "/worldconquest/maps"

    r = requests.get(MAPS_URL)
    map_list = json.loads(r.content)

    return map_list


def getDynamicLabels(map: str):
    dynamic_url = ROOT_URL + f"/worldconquest/maps/{map}/dynamic/public"

    r = requests.get(dynamic_url)
    labels = json.loads(r.content)

    return labels


def getStaticLabels(map: str):
    static_url = ROOT_URL + f"/worldconquest/maps/{map}/static"
    r = requests.get(static_url)
    labels = json.loads(r.content)

    return labels


def calcPointDist(x1, y1, x2, y2):
    return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))


def getLabeledDepots():
    maps = getMaps()

    depots = {}
    for map in maps:
        dynamicLabels = getDynamicLabels(map)
        staticLabels = getStaticLabels(map)

        map.replace('Hex', '')
        depotNames = []
        for dynItem in dynamicLabels['mapItems']:
            if dynItem['iconType'] in ICON_MAP:
                x1 = dynItem['x']
                y1 = dynItem['y']

                depot = {
                    'dist': math.inf,
                    'name': ''
                }

                for statItem in staticLabels['mapTextItems']:
                    x2 = statItem['x']
                    y2 = statItem['y']

                    dist = calcPointDist(x1, y1, x2, y2)
                    if dist < depot['dist']:
                        depot['dist'] = dist
                        depot['name'] = statItem['text']

                depotName = depot['name'] + ' ' + ICON_MAP[dynItem['iconType']]
                depotNames.append(depotName)

        depots[map] = depotNames

    obj = json.dumps(depots)

    with open("depots.json", "w") as file:
        file.write(obj)
    print(obj)


getLabeledDepots()
