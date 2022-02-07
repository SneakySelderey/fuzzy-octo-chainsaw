from math import sin, pi, asin, tanh, log2, radians, tan, log, degrees, atan, e
from numpy import arctanh
from requests import get
from settings import apikey, geocode_server


def LatLonToXY(lat_center, lon_center, zoom):
    c = (256 / (2 * pi)) * 2 ** zoom
    x = c * (radians(lon_center) + pi)
    y = c * (pi - log(tan((pi / 4) + radians(lat_center) / 2)))
    return x, y


def xy2LatLon(lat_center, lon_center, zoom, width_internal, height_internal,
              pxX_internal, pxY_internal):

    x_center, y_center = LatLonToXY(lat_center, lon_center, zoom)

    xPoint = x_center - (width_internal / 2 - pxX_internal)
    yPoint = y_center - (height_internal / 2 - pxY_internal)

    dx, dy = xPoint - x_center, yPoint - y_center
    print(dx, dy)

    c = (256 / (2 * pi)) * 2 ** zoom
    m = (xPoint / c) - pi
    n = -(yPoint / c) + pi

    lon_point = degrees(m)
    lat_point = degrees((atan(e ** n) - (pi / 4)) * 2)

    return lat_point, lon_point


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


def get_full_address(address, postal_code=False):
    """Получение полного адрсеа объекта"""
    obj = get_geocode_object(address)
    if obj is not None:
        address_details = obj['metaDataProperty']['GeocoderMetaData'][
            'Address']
        to_return = address_details['formatted']
        if postal_code:
            to_return += ' , ' + address_details['postal_code']
        return to_return