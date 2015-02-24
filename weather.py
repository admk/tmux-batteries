#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import json
import sys
import urllib.request


location = None
celcius = True
precision = 1
emoji = True
timeout = 5


def fetch_location():
    url = 'http://www.telize.com/geoip'
    response = urllib.request.urlopen(url, timeout=timeout).read()
    geoip = json.loads(response.decode('utf-8'))
    location = '{}, {}'.format(geoip['city'], geoip['country'])
    return location


def fetch(location=None, celcius=True):
    unit = 'metric' if celcius else 'imperial'
    if not location:
        location = fetch_location()
    weather_url = \
        'http://api.openweathermap.org/data/2.5/weather?q={}&units={}'.format(
            location, unit)
    response = urllib.request.urlopen(weather_url, timeout=timeout).read()
    return json.loads(response.decode('utf-8'))


def pictograph(json_str, use_emoji):
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
    code = json_str['weather'][0]['id']
    if code not in json_str:
        code = int(code / 100)
    pict = _pictograph_dict.get(code, '  ')[use_emoji]
    if len(pict) != 1:
        pict = pict[is_daytime()]
    if use_emoji:
        pict += ' '
    return pict


def weather(location, celcius=True, precision=0):
    json_str = fetch(location, celcius)
    unit = '℃' if celcius else '℉'
    use_emoji = emoji and sys.platform == 'darwin'
    return '{pictograph}{temperature:.{precision}f}{unit}'.format(
        pictograph=pictograph(json_str, use_emoji), precision=precision,
        temperature=json_str['main']['temp'], unit=unit)


if __name__ == '__main__':
    sys.stdout.write(weather(location, celcius, precision))
    sys.stdout.flush()
