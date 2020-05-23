from crawler import CrawlWeather
from datetime import datetime, timedelta, date
import pandas as pd
import math
from predict_temperature import predict_temperature
import os.path

def main(show_forecast=False):
    # Crawl weather data including Eisbach Temperature
    Data = CrawlWeather(days_forecast=3)  # 3 and 7 days forecast available
    # Data.eisbach_data.dropna(inplace=True, axis=0)

    # Get previous forecasts if available
    if os.path.exists('./data/forecast.csv'):
        df = pd.read_csv('./data/forecast.csv', index_col='Date', sep=";")
        forecast_exist = True
    else:
        forecast_exist = False

    # Extract minimum and maximum Eisbach temperature:
    # from yesterday
    eisbach_temp_min_yest, eisbach_temp_max_yest = \
    Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['waterTemperature'].min(), \
    Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['waterTemperature'].max()
    # from today
    eisbach_temp_min, eisbach_temp_max = Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())][
                                             'waterTemperature'].min(), \
                                         Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())][
                                             'waterTemperature'].max()
    # assign maximum eisbach temperature from yesterday
    eisbach_temp = eisbach_temp_max_yest
    # eisbach_temp = (eisbach_temp_max_yest + eisbach_temp_min_yest) * 0.5

    # check if temperature from yesterday was available, if not replace by stored predicted temperature or by today's
    # maximum temperature
    if eisbach_temp == None or math.isnan(eisbach_temp):
        if forecast_exist:
            eisbach_temp_min_yest = \
            df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'eisbachTempMax'].astype(
                'float64')[0]
            eisbach_temp_max_yest = \
            df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'eisbachTempMin'].astype(
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

        if (i == 0):
            pred_min = min(pred_min, eisbach_temp_min) # if current Eisbach_temperature is already lower than the prediction
            pred_max = max(pred_max, eisbach_temp_max)  # if current Eisbach_temperature is already higher than the prediction

            # Update data frame with real temperatures from yesterday
            if (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y") in df.index:
                # only update real temperatures if they are available
                if not eisbach_temp_min_yest == None:
                    df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime(
                        "%d.%m.%Y"), df.columns == 'eisbachTempMin'] = eisbach_temp_min_yest
                if not eisbach_temp_max_yest == None:
                    df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime(
                        "%d.%m.%Y"), df.columns == 'eisbachTempMax'] = eisbach_temp_max_yest
        # store data
        data = pd.DataFrame({'perceptionLevel': float(perception_level),
                             'sunshine': float(sunshine),
                             'outsideTempMin': float(min_temp_outside),
                             'outsideTempMax': float(max_temp_outside),
                             'eisbachTempYest': float(eisbach_temp),
                             'eisbachTempMin': float(round(pred_min, 1)),
                             'eisbachTempMax': float(round(pred_max, 1))},
                            index=[forecast_date.strftime("%d.%m.%Y")])

        # check if forecast.csv file exists, if True update forecast data
        if forecast_exist:
            if forecast_date.strftime("%d.%m.%Y") in df.index:
                df.update(data)
            else:
                df = pd.concat([df, data], sort=False)
        else:
            df = data

        eisbach_temp = pred_max # change eisbach temperature from yesterday with current prediction

        if show_forecast:
            print(forecast_date.strftime("%d.%m.%Y") + ": " + str(round(pred_min, 1)) + "°/" + str(round(pred_max, 1)) + "°")

    # save data to json and csv file
    # red = Data.eisbach_data[-36:-1:4][['waterTemperature', 'runoff', 'waterLevel']].sort_index(ascending=True)
    df.to_csv('./data/forecast.csv', index_label='Date', sep=";")
    Data.eisbach_data.to_csv('./data/eisbach_data.csv', index_label='Date', sep=";")
    #df[-Data.days_forecast:][['eisbachTempMin', 'eisbachTempMax']].to_json('./data/forecast_only.json', orient='index')
    return {'forecast': df[['eisbachTempMin', 'eisbachTempMax']][-3:].to_dict('index'), 'hourly': Data.eisbach_data[-33::4].to_dict('index')}

    # Combine json files
    #with open('./data/forecast.json', 'w') as file:
    #    # Write forecast in file
    #    file.write('{ {"forecast": ')
    #    with open('./data/forecast_only.json', 'r') as file_forecast:
    #        for line in file_forecast.readlines():
    #            file.write(str(line))
    #    file.write('}, {"current": {')
    #    i = 0
    #    for column in red.columns:
    #        if i > 0:
    #            file.write(',')
    #        file.write('"{}": {}'.format(column, str(red[column].to_numpy()).replace(" ", ", ")))
    #        i += 1
    #    # current data of eisbach in file
    #    file.write('}}}')

if __name__ == "__main__":
    print(main(show_forecast=True))