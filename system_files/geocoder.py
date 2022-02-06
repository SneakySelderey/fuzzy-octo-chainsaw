from requests import get
from settings import apikey, geocode_server


def get_geocode_object(address):
    """Функция для получения объекта"""
    parameters = {'geocode': address, 'apikey': apikey, 'format': 'json'}
    response = get(geocode_server, params=parameters)
    try:
        return response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']
    except Exception:
        return


def get_address_pos(address):
    """Функция для получения координат объекта"""
    obj = get_geocode_object(address)
    if obj is not None:
        return list(map(float, obj['Point']['pos'].split()))


def get_full_address(address):
    obj = get_geocode_object(address)
    if obj is not None:
        return obj['metaDataProperty']['GeocoderMetaData']['Address']['formatted']


def get_post_index(address):
    obj = get_geocode_object(address)
    if obj is not None:
        return obj['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
