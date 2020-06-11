from crawler import CrawlWeather
from datetime import datetime, timedelta, date
import pandas as pd
import math
from predict_temperature import predict_temperature
import os.path
import json

def main(show_forecast=False):
    # Crawl weather data including Eisbach Temperature
    Data = CrawlWeather(days_forecast=3)  # 3 and 7 days forecast available
    # Data.eisbach_data.dropna(inplace=True, axis=0)

    # Get previous forecasts if available
    forecast_today = True  # parameter to check if forecast prediction was already performed today
    forecast_exist = False  # parameter if forecast.csv exists
    if os.path.exists('./data/forecast.csv'):
        df = pd.read_csv('./data/forecast.csv', index_col='Date', sep=";")
        forecast_exist = True
        if len(df.index) > 2:
            if df.index[-3] == datetime.now().strftime("%d.%m.%Y"):
                forecast_today = False

    # Extract minimum and maximum current Eisbach temperatures:
    eisbach_temp_min, eisbach_temp_max = Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())][
                                             'waterTemperature'].min(), \
                                         Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())][
                                             'waterTemperature'].max()

    eisbach_temp_min = round(eisbach_temp_min*2, 0)*0.5
    eisbach_temp_max = round(eisbach_temp_max*2, 0)*0.5

    # Check if today a forecast was already performed, if yes then skip ne calculation
    if forecast_today:
        eisbach_temp_max_yest = Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['waterTemperature'].max()
        eisbach_temp_min_yest = Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['waterTemperature'].min()
        # assign maximum eisbach temperature from yesterday
        eisbach_temp = eisbach_temp_max_yest

        # check if temperature from yesterday was available, if not replace by stored predicted temperature or by today's
        # maximum temperature
        if eisbach_temp == None or math.isnan(eisbach_temp):
            if forecast_exist:
                if (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y") in df.index:  # Check if forecast data from yesterday is available
                    eisbach_temp_min_yest = \
                    df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'maxWaterTemp'].astype(
                        'float64')[0]
                    eisbach_temp_max_yest = \
                    df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'minWaterTemp'].astype(
                        'float64')[0]
                    eisbach_temp = eisbach_temp_max_yest
            else:
                eisbach_temp = eisbach_temp_max # if no forecast data from yesterday  is available take current max. temperature

        # loop over each single weather forecast entry and calculate eisbach temperature predictions
        for i in range(0, len(Data.weather_forecast)):
            perception_level, sunshine, min_temp_outside, max_temp_outside = Data.weather_forecast[i]
            forecast_date = datetime.now() + timedelta(days=i)

            pred_min, pred_max = predict_temperature(forecast_date.strftime("%d.%m.%Y"), perception_level, sunshine,
                                                     min_temp_outside, max_temp_outside,
                                                     eisbach_temp)

            # Update data frame with real temperatures from yesterday
            if forecast_exist:
                if (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y") in df.index:
                    # only update real temperatures if they are available
                    if not eisbach_temp_min_yest == None:
                        df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime(
                            "%d.%m.%Y"), df.columns == 'minWaterTemp'] = eisbach_temp_min_yest
                    if not eisbach_temp_max_yest == None:
                        df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime(
                            "%d.%m.%Y"), df.columns == 'maxWaterTemp'] = eisbach_temp_max_yest
            # store data
            data = pd.DataFrame({'perceptionLevel': float(perception_level),
                                 'sunshine': float(sunshine),
                                 'minTemp': float(min_temp_outside),
                                 'maxTemp': float(max_temp_outside),
                                 'eisbachTempYest': float(eisbach_temp),
                                 'minWaterTemp': float(round(pred_min, 1)),
                                 'maxWaterTemp': float(round(pred_max, 1))},
                                index=[forecast_date.strftime("%d.%m.%Y")])

            # check if forecast.csv file exists, if True update forecast data
            if forecast_exist:
                if forecast_date.strftime("%d.%m.%Y") in df.index:
                    df.update(data)
                else:
                    df = pd.concat([df, data], sort=False)
            else:
                if i==0:
                    df = data
                else:
                    df = pd.concat([df, data], sort=False)

            eisbach_temp = pred_max # change eisbach temperature from yesterday with current prediction

    # save data to csv file
    # red = Data.eisbach_data[-36:-1:4][['waterTemperature', 'runoff', 'waterLevel']].sort_index(ascending=True)
    df.to_csv('./data/forecast.csv', index_label='Date', sep=";")
    Data.eisbach_data.to_csv('./data/eisbach_data.csv', index_label='Date', sep=";")

    # Check if current eisbach temperature is already lower/higher than the prediction and replace
    # if current Eisbach_temperature is already lower than the prediction
    df.iloc[-3, -2] = min(df.iloc[-3, -2], eisbach_temp_min)
    # if current Eisbach_temperature is already higher than the prediction
    df.iloc[-3, -1] = max(df.iloc[-3, -1], eisbach_temp_max)

    # Prepare data for output
    forecast_return = df[['minWaterTemp', 'maxWaterTemp', 'maxTemp']][-3:]
    forecast_return.index.name = 'Date'

    if show_forecast:
        for i in range(len(forecast_return)):
            print('{}: {}°/{}°'.format(forecast_return.index[i], forecast_return['minWaterTemp'][i], forecast_return['maxWaterTemp'][i]))

    forecast_return.reset_index(inplace=True)
    forecast_return['index'] = ['today', 'tomorrow', 'next']
    forecast_return.set_index('index', inplace=True)

    data_returned = Data.eisbach_data.reset_index()

    data_dict = forecast_return[['Date', 'minWaterTemp', 'maxWaterTemp', 'maxTemp']].to_dict('index')
    data_dict['current'] = {'temp': list(data_returned['airTemperature'].iloc[-9:].to_numpy()),
                            'waterTemp': list(data_returned['waterTemperature'].iloc[-9:].to_numpy()),
                            'waterLevel': Data.eisbach_waterlevel,
                            'runoff': Data.eisbach_runoff }
    # Write to json file
    with open('./data/forecast.json', 'w') as file:
        json.dump(data_dict, file)

if __name__ == "__main__":
    print(main(show_forecast=True))