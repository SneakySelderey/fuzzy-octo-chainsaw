from math import pi, radians, tan, log, degrees, sin, sqrt, atan
import math
from requests import get
from settings import apikey, geocode_server, search_api_server, apikey_org, \
    r_major, r_minor, temp
import geopy.distance


def lonToX(lon):
    """Возвращает координату долготы"""
    return r_major * radians(lon)


def xToLon(x):
    """Возвращает долготу координаты"""
    return degrees(x / r_major)


def yToLat(y):
    """Возвращает широту координаты"""
    iz_lon = y / r_major
    eccent = sqrt(1 - temp ** 2)
    lon = 0
    for e in range(100):
        lon = -2 * atan((math.e ** -iz_lon) *
                             (((1 - eccent * sin(lon)) / (
                                     1 + eccent * sin(lon))) ** (
                                  eccent / 2))) + pi / 2
    return round(degrees(lon), 7)


def latToY(lat):
    """Возвращает коорднату широты"""
    lat = max(-89.5, min(lat, 89.5))
    e = sqrt(1 - temp ** 2)
    phi = radians(lat)
    sinphi = sin(phi)
    con = ((1.0 - e * sinphi) / (1.0 + e * sinphi)) ** (e / 2)
    v = log(tan((pi / 2 + phi) / 2) * con)
    return r_major * v


def get_coeff(z):
    """Возвращает коэффициент масштабирования"""
    return 2 ** (8 + z) / (r_major * pi)


def get_distance(p1, p2):
    """Возвращает расстояние между двумя точками"""
    return geopy.distance.distance(p1, p2).m


def get_organization(pos):
    """Функция, возвращающая ближайшую организауцию к точке на карте"""
    parameters = {"apikey": apikey_org, "text": ','.join(map(str, pos[::-1])),
                  "lang": "ru_RU", "type": "biz"}

    response = get(search_api_server, params=parameters)
    if response:
        return response.json()['features']


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