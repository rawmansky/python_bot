import requests
from pprint import pprint

def get_wather_for_city(city, forcast):
    params = {
        'q': city,#'Vladivostok,ru',
        'appid': '17704ff3c5f002fcf6356e54ffae623f',
        'units': 'metric',
        'lang': 'ru'
    }
    #?q=Moscow,ru&appid=API_KEY
    if forcast:
        url = 'http://api.openweathermap.org/data/2.5/forecast'
    else:
        url = 'http://api.openweathermap.org/data/2.5/weather'

    try:
        result = requests.get(url, params=params)
        try:
            result.raise_for_status()
        #print(result.json())#result.starus_code #text
            return result.json()
        except (requests.HTTPError):
            return False
    except(requests.exceptions.RequestException):
        return False
    
if __name__ == "__main__": 
    weather = get_wather_for_city('Vladivosto,ru', True)
    #pprint(weather)
    if weather:
        try:
            print(weather['city']['name'])
            for hour in weather['list']:
                ###pprint(hour)
                print('{} temp:{}'.format(hour['dt_txt'], hour['main']['temp']))#main ['weather'] ['dt_txt'] + ' ' + weather['list']['temp']
        except:
            print(weather['main']['temp_max'])
    else:
        print('Somethig went wrong')

#17704ff3c5f002fcf6356e54ffae623f