#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import pickle
import json
import sys
import urllib
import urllib.request


location = None
celcius = True
precision = 1
emoji = True
timeout = 5

tmp_file = '/tmp/tmux_batteries_weather.pkl'


def fetch_location():
    url = 'https://freegeoip.net/json/'
    response = urllib.request.urlopen(url, timeout=timeout).read()
    geoip = json.loads(response.decode('utf-8'))
    return geoip['latitude'], geoip['longitude']


def fetch(location=None, celcius=True):
    unit = 'metric' if celcius else 'imperial'
    if not location:
        lat, lon = fetch_location()
        location = 'lat={}&lon={}'.format(lat, lon)
    weather_url = \
        'http://api.openweathermap.org/data/2.5/weather?{}&units={}'.format(
            location, unit)
    response = urllib.request.urlopen(weather_url, timeout=timeout).read()
    return json.loads(response.decode('utf-8'))


def cached_fetch(location=None, celcius=True):
    try:
        json_data = fetch(location, celcius)
        with open(tmp_file, 'wb') as f:
            pickle.dump(json_data, f)
        return json_data, False
    except urllib.error.URLError:
        with open(tmp_file, 'rb') as f:
            return pickle.load(f), True


def pictograph(json_data, use_emoji):
    def is_daytime():
        from datetime import datetime
        return 6 <= datetime.now().hour < 18
    _pictograph_dict = {
        2: '☈⚡',           # thunderstorm
        3: '☂🌂',           # drizzle
        5: '☔☔',           # rain
        6: '❄⛄',           # snow
        7: '〰🌁',         # mist/smoke/haze/sand/fog
        8: '☁⛅',           # clouds
        9: '颶🌀',         # extreme
        # specials
        800: ['☽☼', '🌜🌞']  # clear sky
    }
    code = json_data['weather'][0]['id']
    if code not in json_data:
        code = int(code / 100)
    pict = _pictograph_dict.get(code, '  ')[use_emoji]
    if len(pict) != 1:
        pict = pict[is_daytime()]
    if use_emoji:
        pict += ' '
    return pict


def weather(location=None, celcius=True, precision=0):
    json_data, is_cached = cached_fetch(location, celcius)
    unit = '℃' if celcius else '℉'
    temp = '{:.{prec}f}'.format(json_data['main']['temp'], prec=precision)
    if is_cached:
        temp = '~' + temp
    pict = pictograph(json_data, emoji and sys.platform == 'darwin')
    return '{pict}{temp}{unit}'.format(pict=pict, temp=temp, unit=unit)


if __name__ == '__main__':
    sys.stdout.write(weather(location, celcius, precision))
    sys.stdout.flush()
