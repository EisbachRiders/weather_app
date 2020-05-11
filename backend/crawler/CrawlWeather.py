import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class CrawlWeather:
    def __init__(self, update=True):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/73.1'}
        self.eisbach_temperatures = []
        self.weather_forecast = []

        if update:
            self.getData()

    def getTemperature(self, date_start, date_end):
        url = "https://www.gkd.bayern.de/de/fluesse/wassertemperatur/isar/muenchen-himmelreichbruecke-16515005/monatswerte/tabelle?beginn=" + date_start.strftime("%d.%m.%Y") + "&ende=" + date_end.strftime("%d.%m.%Y")
        r = requests.get(url)
        doc = BeautifulSoup(r.text, "html.parser")

        data = doc.select(".row2 .center")

        min_Temp = None
        max_Temp = None

        for element in data:
            if not element.text =="--":
                if min_Temp == None:
                    min_Temp = float(element.text.replace(',', '.'))
                else:
                    min_Temp = min(min_Temp, float(element.text.replace(',', '.')))
                if max_Temp == None:
                    max_Temp =float(element.text.replace(',', '.'))
                else:
                    max_Temp = max(max_Temp, float(element.text.replace(',', '.')))

        return (min_Temp,  max_Temp)

    def getWeather(self):

        #url = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/flughafen-muenchen-franz-josef-strauss-muc/DE0003033027.html'
        url  = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/muenchen/DE0006515.html'
        r = requests.get(url)

        doc = BeautifulSoup(r.text, "html.parser")
        data = doc.select(".spaces-weather-grid .swg-row-wrapper")
        param_min = []
        param_max = []
        param_rain = []
        count= 0

        # Get temperatures and rain
        for element in data:
            if count==0 or count==5 or count==10:
                data_max = element.select(".swg-col-temperature .swg-text-large")
                data_min = element.select(".swg-col-temperature .swg-text-small")
                data_rain= element.select(".swg-col-wv2")

                param_min.append(float(data_min[0].text.strip().split('°')[0].split('/\u2009')[1].replace(',', '.')))
                param_max.append(float(data_max[0].text.split('°')[0].strip().replace(',', '.')))
                param_rain.append(float(data_rain[0].text.split('l/')[0].strip().replace(',', '.')))

            count += 1

        # Get sun hours
        param_sun =[]
        liste_son = doc.select(".spaces-weather-grid .swg-row-info")
        for element in liste_son:
            if "Sonne" in element.text:
                # Check which phrase is forecasting the sun hours and change to right number format
                if ("Heute gibt es bis zu" in element.text.split("Sonne")[0]):
                    param_sun.append(float(element.text.split("Sonne")[0].split("Heute gibt es bis zu")[1].replace(',', '.')))
                elif ("zeigt sich nur etwa" in element.text.split("Sonne")[1]):
                    param_sun.append(float(element.text.split("Sonne")[1].split("zeigt sich nur etwa ")[1].split(" Stunde")[0].replace(',', '.')))
                elif ("ist heute fast nicht zu sehen" in element.text.split("Sonne")[1]):
                    param_sun.append(float(0.0))
                else:
                    param_sun.append(float(element.text.split("Sonne")[0].split("Freuen Sie sich auf bis zu")[1].replace(',', '.')))

        forecast_data = []

        for i in range(0, len(param_min)):
            forecast_data.append((param_rain[i], param_sun[i], param_min[i], param_max[i]))

        return forecast_data

    def getData(self):
        self.weather_forecast = self.getWeather()
        # Get Temperatures from yesterday
        self.eisbach_temperatures = [self.getTemperature(datetime.now() - timedelta(days=1), datetime.now()- timedelta(days=1))]#Get temperatures from yesterday
        # Get Current Eisbach Temperatures
        self.eisbach_temperatures.append(self.getTemperature(datetime.now(), datetime.now())) # Get temperatures from yesterday

