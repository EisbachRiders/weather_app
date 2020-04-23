import numpy as np
from crawler import CrawlWeather
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def predict_temperature(date, perception_level, sunshine, min_temp_outside, max_temp_outside, eisbach_temp):
    """
    function predict_temperature(year, month, rain, sunshine, min_temp, max_temp)
    returns maximum forcast temperature of Eisbach for the following input parameters

    year = current year
    month = current month as numeric
    perception_level = expected perception level for the day [mm]
    sunshine = Sunshine duration in [h]
    min_temp_outside = Minimum temperature in [°C]
    max_temp_outside = Maximum temperature in [°C]
    temp_eis_yest = Eisbach Temperature the day before [°C]
    """
    # adapted input
    year  = int(date.split('.')[2])
    month = int(date.split('.')[1])
    input = np.array([year, month, perception_level, sunshine, min_temp_outside, max_temp_outside, eisbach_temp])

    coeff_min = np.array([0.00671369,  0.05433055, -0.01699897, -0.0091107,   0.04654794,  0.04494732,
                          0.80392883])  # determined in create_model.py
    intercept_min = -13.801013453736768  # determined in create_model.py

    coeff_max = np.array([0.0037455,  0.02092407, -0.00372701, 0.04690195, 0.06081745, 0.03382019, 0.84128262]) # determined in create_model.py
    intercept_max = -7.175286431561844 # determined in create_model.py

    return (coeff_min.dot(input)+intercept_min, coeff_max.dot(input)+intercept_max)

# Crawl weather data including Eisbach Temperature
Data = CrawlWeather()

# Extract minimum and maximum Eisbach temperature from today
eisbach_temp_min_yest, eisbach_temp_max_yest = Data.eisbach_temperatures[0]
eisbach_temp_min, eisbach_temp_max = Data.eisbach_temperatures[1]
eisbach_temp = eisbach_temp_max_yest
# Get forecast
df = pd.read_csv('forecast.csv', index_col='Date', sep=";")

for i in range(0, len(Data.weather_forecast)):
    perception_level, sunshine, min_temp_outside, max_temp_outside = Data.weather_forecast[i]
    date = datetime.now() + timedelta(days=i)
    pred_min, pred_max = predict_temperature(date.strftime("%d.%m.%Y"), perception_level, sunshine, min_temp_outside, max_temp_outside,
                        eisbach_temp)

    if (i==0):
        pred_min = min(pred_min, eisbach_temp_min) # if current Eisbach_temperature is already lower than the prediction
        pred_max = max(pred_max, eisbach_temp_max)  # if current Eisbach_temperature is already higher than the prediction

        # Update data frame with real temperatures from yesterday
        if (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y") in df.index:
            df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), df.columns == 'Eisbach_Temp_min'] = eisbach_temp_min_yest
            df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), df.columns == 'Eisbach_Temp_max'] = eisbach_temp_max_yest

    data = pd.DataFrame({'perception_level': float(perception_level),
                         'Sunshine': float(sunshine),
                         'Outside_Temp_min': float(min_temp_outside),
                         'Outside_Temp_max': float(max_temp_outside),
                         'Eisbach_Temp_Yest': float(eisbach_temp),
                         'Eisbach_Temp_min': float(round(pred_min, 1)),
                         'Eisbach_Temp_max': float(round(pred_max, 1))},
                         index = [date.strftime("%d.%m.%Y")])


    if date.strftime("%d.%m.%Y") in df.index:
        df.update(data)
    else:
        df = pd.concat([df, data], sort=False)

    eisbach_temp = round(pred_max, 1)
    #print(date.strftime("%d.%m.%Y") + ": " + str(round(pred_min, 1)) + "°/" + str(round(pred_max, 1)) + "°") # taken data from meteomedia.de

df.to_csv('forecast.csv', index_label='Date', sep=";")
# Models old
# Forecast model without the Eisbach temperature day before
    # coeff = np.array([0.06144129, 0.20976543, 0.02161775, 0.11419631, 0.33478473, 0.2672007]) # determined in create_model.py
    # intercept = -119.94585765676487 # determined in create_model.py
