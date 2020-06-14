import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os.path
from ftplib import FTP

class CrawlWeather:
    def __init__(self, update=True, days_forecast=3):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/73.1'}
        # self.eisbach_data = [] # data_frame,
        self.weather_forecast = []
        self.days_forecast = days_forecast

        self.getData(update) # if update==True, the current weather forecast is also crawled. Eisbach data is always called

    def getCreekData(self, date_start, date_end):
        #Connect to FTP
        ftp = FTP('w012ebdc.kasserver.com')
        ftp.login('f00e94e0','funtimes310')
        ftp.cwd('eisbach-riders/forecast')
        ftp.retrbinary("RETR " + 'eisbach_data.csv', open('./tmp/eisbach_data.csv', 'wb').write)
        ftp.quit()

        categories = ['wassertemperatur', 'abfluss', 'wasserstand', 'airtemperature']
        labels = {'wassertemperatur': 'waterTemperature', 'abfluss': 'runoff', 'wasserstand': 'waterLevel',
                  'airtemperature': 'airTemperature'}

        for category in categories:
            if category == 'airtemperature':
                url = 'https://www.gkd.bayern.de/de/meteo/lufttemperatur/passau/eichenried-200114/messwerte/tabelle?zr=woche&art=&beginn=' + date_start.strftime(
                    "%d.%m.%Y") + '&ende=' + date_end.strftime("%d.%m.%Y")
            else:
                url = "https://www.gkd.bayern.de/de/fluesse/" + category + "/isar/muenchen-himmelreichbruecke-16515005/monatswerte/tabelle?beginn=" + date_start.strftime(
                    "%d.%m.%Y") + "&ende=" + date_end.strftime("%d.%m.%Y")
            r = requests.get(url)
            doc = BeautifulSoup(r.text, "html.parser")
            # data = doc.select(".row2")
            data = doc.findAll('table')[1].findAll('tr')

            for i in range(1, len(data)):
                element = data[i]
                date_val = element.text.split(' ')[0]
                time_val = element.text.split(' ')[1][0:5]
                cat_val = element.text.split(' ')[1][5:]

                if not cat_val == "--":
                    cat_val = float(cat_val.replace(',', '.'))
                    if category == 'abfluss' or category == 'wasserstand':
                        break
                else:
                    cat_val = float('NaN')

                if i == 1:
                    value_list = np.array([[datetime(int(date_val.split('.')[2]), int(date_val.split('.')[1]),
                                                     int(date_val.split('.')[0]),
                                                     int(time_val.split(':')[0]), int(time_val.split(':')[1]), 0),
                                            cat_val]])
                else:
                    value_list = np.append(value_list, [
                        [datetime(int(date_val.split('.')[2]), int(date_val.split('.')[1]), int(date_val.split('.')[0]),
                                  int(time_val.split(':')[0]), int(time_val.split(':')[1]), 0), cat_val]], axis=0)

            if category == 'wassertemperatur':
                creek_data = pd.DataFrame({labels[category]: value_list[:, 1]}, index=value_list[:, 0])
            elif category == 'abfluss':
                self.eisbach_runoff = cat_val
            elif category == 'wasserstand':
                self.eisbach_waterlevel = cat_val
            else:
                creek_data = creek_data.merge(
                    pd.DataFrame({labels[category]: value_list[:, 1]}, index=value_list[:, 0]), how='left',
                    left_index=True, right_index=True)

        # if crawling data delivers not the right hour format (not full and half hours), shifting data by 15min
        # creek_data.index = creek_data.index.map(lambda x: x+timedelta(minutes=15.0) if (x.minute == 15) or (x.minute == 45) else x)

        # After crawling current data filter only even full hours (reduce data set)
        creek_data.dropna(inplace=True)
        creek_data = creek_data[(creek_data.index.hour % 2 == 0) & (creek_data.index.minute == 0)]
        # After crawling current data check with stored data
        if os.path.exists('./tmp/eisbach_data.csv'):
            def dateparse(string_timestamp):
                return datetime.strptime(string_timestamp, "%Y-%m-%d %H:%M:%S")

            creek_data_stored = pd.read_csv('./tmp/eisbach_data.csv', delimiter=";", index_col='Date',
                                            parse_dates=True, date_parser=dateparse)
            # add new values
            creek_data_stored = pd.concat(
                [creek_data_stored, creek_data[~creek_data.index.isin(creek_data_stored.index)]])
            # update values with current eisbach data
            creek_data_stored.update(creek_data[['waterTemperature', 'airTemperature']])
            creek_data = creek_data_stored

        return creek_data

    def getWeatherForecast(self):
        #url = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/flughafen-muenchen-franz-josef-strauss-muc/DE0003033027.html'
        #url  = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/3_tagesvorhersage/deutschland/muenchen/DE0006515.html'
        url = 'https://www.wetter.com/wetter_aktuell/wettervorhersage/' + str(self.days_forecast)  + '_tagesvorhersage/deutschland/muenchen/DE0006515.html'
        r = requests.get(url)
        doc = BeautifulSoup(r.text, "html.parser")

        # Get current air temperature
        #current_air_temperature = float(doc.find_all(class_="text--white beta")[0].text.split("°")[0])

        # Get forecast data
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

    def getData(self, update = True):
        # Get current temperature and weather forecast for defined days
        if update:
            # Get weather forecast for defined days
            self.weather_forecast = self.getWeatherForecast()

        # Get Eisbach Data and air temperature data
        self.eisbach_data = self.getCreekData(datetime.now() - timedelta(days=1), datetime.now())

        self.eisbach_data = self.eisbach_data.sort_index(ascending=True)





