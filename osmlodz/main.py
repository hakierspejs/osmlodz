#!/usr/bin/env python

import json
import xml.etree.ElementTree as ET
import urllib.parse
import dataclasses

import requests
from flask import Flask, render_template


app = Flask(__name__)


@dataclasses.dataclass
class Marker:
    name: str
    opening_hours: str
    amenity: str
    shop: str
    street: str
    housenumber: str
    lat: str
    lon: str
    id_: str


def get_open_places(city_name):
    query = f'''\
    area[name="{city_name}"]->.city;
    node(area.city)[opening_hours];
    out meta;'''

    url = 'https://overpass-api.de/api/interpreter?data=' + \
        urllib.parse.quote(query)

    response = requests.get(url)

    root = ET.fromstring(response.text)

    markers = []

    for node in root:
        lat = node.attrib.get('lat')
        lon = node.attrib.get('lon')

        if lat and lon:

            tags_to_get = ['name', 'opening_hours', 'amenity',
                           'shop', 'addr:street', 'addr:housenumber']
            tags = {
                tag.attrib.get('k', '').split(':')[-1]: tag.attrib.get('v')
                for tag in node
                if tag.attrib.get('k') in tags_to_get
            }

            for tag in tags_to_get:
                tag = tag.split(':')[-1]
                if tag not in tags:
                    tags[tag] = None

            tags['lat'] = lat
            tags['lon'] = lon
            tags['id_'] = node.attrib.get('id')

            marker = Marker(**tags)

            markers.append(marker)

    return markers


OPEN_PLACES = get_open_places('Łódź')


def build_json_html(markers):
    ret = []
    for marker in markers:
        geo_url = f'geo:{marker.lat},{marker.lon}'
        geo_title = f'{marker.lat}&deg;N {marker.lon}&deg;E'
        osm_url = f'https://www.openstreetmap.org/node/{marker.id_}/'

        desc = []
        ignore_tags = {'lat', 'lon', 'street', 'amenity', 'id_', 'housenumber'}
        tags = {
            k: v
            for k, v in marker.__dict__.items()
            if ':' not in k and k not in ignore_tags and v is not None
        }
        if marker.street is not None and marker.house_number is not None:
            tags['address'] = f'{marker.street} {marker.house_number}'
        for k, v in tags.items():
            desc.append(f'<b>{k}:</b> {v}')
        desc = list(sorted(desc))

        ret.append([marker.lat, marker.lon, '<br>'.join([
            f'<big><a href="{geo_url}">{geo_title}</a></big>',
            *desc,
            f'<a href="{osm_url}">OSM: {marker.id_}</a><br>',
        ])])
    return json.dumps(ret, indent='\t')


@app.route('/')
def main_view():
    return render_template('index.html', data=build_json_html(OPEN_PLACES))


if __name__ == '__main__':
    print(build_json_html(OPEN_PLACES))
    app.run(host='0.0.0.0')
