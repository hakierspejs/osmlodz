#!/usr/bin/env python

import json
import xml.etree.ElementTree as ET
import urllib.parse

import requests
from flask import Flask, render_template


app = Flask(__name__)


query = '''\
area[name="Łódź"]->.lodz;
node(area.lodz)[opening_hours];
out meta;'''

url = 'https://overpass-api.de/api/interpreter?data=' + urllib.parse.quote(query)

response = requests.get(url)

root = ET.fromstring(response.text)

markers = []

for node in root:
    lat = node.attrib.get('lat')
    lon = node.attrib.get('lon')

    if lat and lon:
        id_ = node.attrib.get('id')

        tags_to_get = ['name', 'opening_hours', 'amenity', 'shop', 'addr:street', 'addr:housenumber']
        tags = {tag.attrib.get('k'): tag.attrib.get('v') for tag in node if tag.attrib.get('k') in tags_to_get}

        street = tags.get('addr:street')
        house_number = tags.get('addr:housenumber')
        if street and house_number:
            tags['address'] = street + ' ' + house_number

        description = [
            '<big><a href="geo:{lat},{lon}">{lat}&deg;N {lon}&deg;E</a></big>'.format(lat=lat, lon=lon),
            *sorted('<b>{}:</b> {}'.format(k, v) for k, v in tags.items() if ':' not in k),
            '<a href="https://www.openstreetmap.org/node/{id_}/">OSM: {id_}</a><br>'.format(id_=id_),
        ]

        markers.append([lat, lon, '<br>'.join(description)])

data = json.dumps(markers, indent='\t')


@app.route('/')
def main_view():
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
