import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class CrawlWeather:
    def __init__(self, update=True, days_forecast=3):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/73.1'}
        # self.eisbach_data = [] # data_frame,
        self.weather_forecast = []
        self.days_forecast = days_forecast

        if update:
            self.getData()

    def getCreekData(self, date_start, date_end):
        categories = ['wassertemperatur', 'abfluss', 'wasserstand']
        labels = {'wassertemperatur': 'water_temperature', 'abfluss': 'runoff', 'wasserstand': 'water_level'}

        for category in categories:
            url = "https://www.gkd.bayern.de/de/fluesse/" + category + "/isar/muenchen-himmelreichbruecke-16515005/monatswerte/tabelle?beginn=" + date_start.strftime(
                "%d.%m.%Y") + "&ende=" + date_end.strftime("%d.%m.%Y")
            r = requests.get(url)

            doc = BeautifulSoup(r.text, "html.parser")
            data = doc.select(".row2")

            i = 0
            for element in data:
                date_val = element.text.split(' ')[0]
                time_val = element.text.split(' ')[1][0:5]
                cat_val = element.text.split(' ')[1][5:]

                if not cat_val == "--":
                    cat_val = float(cat_val.replace(',', '.'))
                else:
                    cat_val = float('NaN')

                if i == 0:
                    value_list = np.array([[datetime(int(date_val.split('.')[2]), int(date_val.split('.')[1]), int(date_val.split('.')[0]),
                                                     int(time_val.split(':')[0]), int(time_val.split(':')[1]), 0), cat_val]])
                    i = 1
                else:
                    value_list = np.append(value_list, [[datetime(int(date_val.split('.')[2]), int(date_val.split('.')[1]), int(date_val.split('.')[0]),
                                                     int(time_val.split(':')[0]), int(time_val.split(':')[1]), 0), cat_val]], axis=0)

            if category == 'wassertemperatur':
                creek_data = pd.DataFrame({labels[category]: value_list[:, 1]}, index=value_list[:, 0])
            else:
                creek_data = pd.concat(
                    [creek_data, pd.DataFrame({labels[category]: value_list[:, 1]}, index=value_list[:, 0])], axis=1)

                # old code, only determine min, max temperature
                #if not element.text =="--":
                    #if min_Temp == None:
                    #    min_Temp = float(element.text.replace(',', '.'))
                    #else:
                    #    min_Temp = min(min_Temp, float(element.text.replace(',', '.')))
                    #if max_Temp == None:
                    #    max_Temp =float(element.text.replace(',', '.'))
                    #else:
                    #    max_Temp = max(max_Temp, float(element.text.replace(',', '.')))

        return creek_data

    def getWeather(self):
        #url = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/flughafen-muenchen-franz-josef-strauss-muc/DE0003033027.html'
        #url  = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/muenchen/DE0006515.html'
        url = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/' + str(self.days_forecast)  + '_tagesvorhersage/deutschland/muenchen/DE0006515.html'
        r = requests.get(url)

        doc = BeautifulSoup(r.text, "html.parser")
        data = doc.select(".spaces-weather-grid .swg-row-wrapper")
        param_min = []
        param_max = []
        param_rain = []
        count = 0

        crawl_ids = np.arange(0, self.days_forecast*5, 5)

        # Get temperatures and rain
        for element in data:
            if count in crawl_ids:
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
        # Get Eisbach Data
        self.eisbach_data = self.getCreekData(datetime.now() - timedelta(days=1), datetime.now())#Get temperatures from yesterday


