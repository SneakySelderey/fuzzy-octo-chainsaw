from math import pi, radians, tan, log, degrees, atan, e, asin, tanh, sin
import utm
from numpy import arctanh
from requests import get
from settings import apikey, geocode_server


def tile2latlon(x, y, z):
    L = 85.05112878
    lon = ((x / 2.0**(z+7) )-1) * 180
    lat = 180/pi * (asin(tanh(-pi/2**(z+7)*y + arctanh(sin(pi/180*L)))))
    return [lat, lon]


def latlon2tile2(lat, lon, z):
    L = 85.05112878
    x = int((lon/180 + 1) * 2**(z+7))
    y = int( (2**(z+7) / pi * ( -arctanh(sin(pi*lat/180)) + arctanh(sin(pi*L/180)) ) ))
    return [x,y]


def LatLonToXY(lat_center, lon_center, zoom):
    """Географические координаты в декартовы"""
    c = (256 / (2 * pi)) * 2 ** zoom
    x = c * (radians(lon_center) + pi)
    y = c * (pi - log(tan((pi / 4) + radians(lat_center) / 2)))
    return x, y


def xy2LatLon(lat_center, lon_center, zoom, pxX_internal, pxY_internal):
    """Декартовы координты в географические"""

    x_center, y_center, num, let = utm.from_latlon(lat_center, lon_center)
    print(tile2latlon(x_center, y_center, 1))

    px = int(x_center / 2 ** (zoom - 6.439))
    py = int(y_center / 2 ** (zoom - 4.875))
    print(px, py)
    dx = (px - pxX_internal) * 2 ** (zoom - 8)
    dy = (py - pxY_internal) * 2 ** (zoom - 8)

    xPoint = x_center + dx
    yPoint = y_center + dy

    return utm.to_latlon(xPoint, yPoint, num, let)


def xytoLatLon(lat_center, lon_center, zoom, width_internal, height_internal,
              pxX_internal, pxY_internal):
    """Декартовы координты в географические"""

    z = utm.from_latlon(lat_center, lon_center)

    x_center, y_center = LatLonToXY(lat_center, lon_center, zoom)
    print(x_center, y_center)
    print(z)

    ww = utm.to_latlon(z[0], z[1], 39, 'P')
    print(ww)
    print(utm.to_latlon(z[0], z[1], 40, 'P'))
    print()

    print(x_center / 2 ** (zoom - 1), y_center / 2 ** (zoom - 1))

    xPoint = x_center - (width_internal / 2 - pxX_internal)
    yPoint = y_center - (height_internal / 2 - pxY_internal)
    print(int(x_center / 2 ** (zoom - 1)) - pxY_internal, int(y_center / 2 ** (zoom - 1)) - pxX_internal)
    xPoint = x_center + (int(x_center / 2 ** (zoom - 1)) - pxY_internal) * 2 ** (zoom - 20)
    yPoint = y_center + (int(y_center / 2 ** (zoom - 1)) - pxY_internal) * 2 ** (zoom - 20)

    print(x_center, xPoint)
    print(y_center, yPoint)
    print()

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