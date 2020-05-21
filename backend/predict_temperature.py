from crawler import CrawlWeather
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import math

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

    # Model based on absolute values
    coeff_min = np.array([0.00671369,  0.05433055, -0.01699897, -0.0091107,   0.04654794,  0.04494732,
                        0.80392883])  # determined in create_model.py
    intercept_min = -13.801013453736768  # determined in create_model.py

    coeff_max = np.array([0.0037455,  0.02092407, -0.00372701, 0.04690195, 0.06081745, 0.03382019, 0.84128262]) # determined in create_model.py
    intercept_max = -7.175286431561844 + 0.4 # determined in create_model.py

    pred_min= (coeff_min.dot(input)+intercept_min)
    pred_max = (coeff_max.dot(input)+intercept_max)

   # coeff_min = np.array([0.05483041, -0.016345, -0.01008393, 0.04782776, 0.04187978, 0.8050485])  # determined in create_model.py
    #intercept_min = -0.28621030349744636  # determined in create_model.py

   # coeff_max = np.array([0.02163978, -0.00365438, 0.04602888, 0.06163503, 0.03266243, 0.84112031])  # determined in create_model.py
   # intercept_max = 0.36795459680280196 #determined in create_model.py, +0.4 manual calibration based on analysis of forecasts using standard deviation

    #pred_min = (coeff_min.dot(input[1:]) + intercept_min)
    #pred_max = (coeff_max.dot(input[1:]) + intercept_max)

    # Model based on absolute values using mean temperature of yesterday
    #coeff_min = np.array([0.00484214, 0.03471175, -0.01330399, -0.00724732, 0.05270956, 0.03085562,
    #                      0.84009748])  # determined in create_model.py
    #intercept_min = -9.777221997859076  # determined in create_model.py

    #coeff_max = np.array([3.13546713e-03, 3.40500156e-03, -1.40610706e-04, 5.00723398e-02,
    #                      6.93541163e-02, 2.54861034e-02, 8.65755471e-01])  # determined in create_model.py
    #intercept_max = -5.624453431216242  # determined in create_model.py

    #pred_min= (coeff_min.dot(input)+intercept_min)
    #pred_max = (coeff_max.dot(input)+intercept_max)

    # Model based on absolute values reduced without month and year impact
    #coeff_min = np.array([0.01472884, -0.07693521, -0.01854033,  0.03439843,  0.94663809])  # determined in create_model.py
    #intercept_min = -0.21604758181539374  # determined in create_model.py

    #coeff_max = np.array([0.03120086, -0.01669777, -0.00640453,  0.02463498,  0.97910236]) # determined in create_model.py
    #intercept_max = 0.256595732133281 # determined in create_model.py

    #pred_min= (coeff_min.dot(input[2:])+intercept_min)
    #pred_max = (coeff_max.dot(input[2:])+intercept_max)

    #return (coeff_min.dot(input)+intercept_min, coeff_max.dot(input)+intercept_max)

    # Model based on relative values and current temperature
    #coeff_min = np.array([-0.00156414, 0.00934064, 0.0009266,  -0.00420075,  0.00014419,  0.00738503,
    #                      -0.00282276])  # determined in create_model.py
    #intercept_min = 2.9807046899104903  # determined in create_model.py

    #coeff_max = np.array([5.13029312e-05,  2.56985254e-03, 2.51015435e-03, 9.85807662e-04, -1.44815570e-03, 3.07148536e-03, -3.60185565e-03]) # determined in create_model.py
    #intercept_max = -0.07738353005475171 # determined in create_model.py

    # Model based on relative values
    #input = np.array([year, month, perception_level, sunshine, min_temp_outside, max_temp_outside])
    #coeff_min = np.array([-0.00173306,  0.00878944,  0.00095759, -0.00457154, -0.00064343,  0.0064828
    #                      ])  # determined in create_model.py
    #intercept_min = 3.310302355133679 # determined in create_model.py

    #coeff_max = np.array([-0.00016424,  0.00186651,  0.0025497,   0.00051268, -0.00245315,  0.00192023 ]) # determined in create_model.py
    #intercept_max = 0.3431845685560249 # determined in create_model.py

    #pred_min= (1+coeff_min.dot(input)+intercept_min)*eisbach_temp
    #pred_max = (1+coeff_max.dot(input)+intercept_max)*eisbach_temp

    return (round(pred_min*2,0)*0.5, round(pred_max*2,0)*0.5)

# Crawl weather data including Eisbach Temperature
Data = CrawlWeather(days_forecast=3) # 3 and 7 days forecast available
Data.eisbach_data.dropna(inplace=True, axis=0)

# Comparison with Meteomedia
# Data.eisbach_temperatures = [(11.2, 15.6), (300, -100)]
# Data.weather_forecast = [(2.1, 4.0, 13, 22)]

# Get previous forecasts
df = pd.read_csv('forecast.csv', index_col='Date', sep=";")

# Extract minimum and maximum Eisbach temperature from today
eisbach_temp_min_yest, eisbach_temp_max_yest = Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['water_temperature'].min(), \
                                               Data.eisbach_data[Data.eisbach_data.index < pd.to_datetime(date.today())]['water_temperature'].max()
eisbach_temp_min, eisbach_temp_max = Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())]['water_temperature'].min(),\
                                     Data.eisbach_data[Data.eisbach_data.index >= pd.to_datetime(date.today())]['water_temperature'].max()
eisbach_temp = eisbach_temp_max_yest
#eisbach_temp = (eisbach_temp_max_yest + eisbach_temp_min_yest) * 0.5

if eisbach_temp == None or math.isnan(eisbach_temp):
    eisbach_temp_min_yest = df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'Eisbach_Temp_max'].astype('float64')[0]
    eisbach_temp_max_yest = df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), 'Eisbach_Temp_min'].astype('float64')[0]
    eisbach_temp = eisbach_temp_max_yest


for i in range(0, len(Data.weather_forecast)):
    perception_level, sunshine, min_temp_outside, max_temp_outside = Data.weather_forecast[i]
    date = datetime.now() + timedelta(days=i)

    pred_min, pred_max = predict_temperature(date.strftime("%d.%m.%Y"), perception_level, sunshine, min_temp_outside, max_temp_outside,
                        eisbach_temp)

    if (i==0):
        #pred_min = min(pred_min, eisbach_temp_min) # if current Eisbach_temperature is already lower than the prediction
        #pred_max = max(pred_max, eisbach_temp_max)  # if current Eisbach_temperature is already higher than the prediction


        # Update data frame with real temperatures from yesterday
        if (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y") in df.index:
            # only update real temperatures if they are available
            if not eisbach_temp_min_yest == None:
                df.loc[df.index == (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"), df.columns == 'Eisbach_Temp_min'] = eisbach_temp_min_yest
            if not eisbach_temp_max_yest == None:
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

    #eisbach_temp = round(pred_max, 1)
    eisbach_temp = pred_max
    print(date.strftime("%d.%m.%Y") + ": " + str(round(pred_min, 1)) + "°/" + str(round(pred_max, 1)) + "°") # taken data from meteomedia.de

# save data to json
Data.eisbach_data[-48:].to_json('./data/current_eisbach_data.json', orient='index')  # last 24h, 2 entries per hour
df.to_csv('forecast.csv', index_label='Date', sep=";")
df[-Data.days_forecast:][['Eisbach_Temp_min', 'Eisbach_Temp_max']].to_json('./data/forecast.json', orient='index')
# Models old
# Forecast model without the Eisbach temperature day before
    # coeff = np.array([0.06144129, 0.20976543, 0.02161775, 0.11419631, 0.33478473, 0.2672007]) # determined in create_model.py
    # intercept = -119.94585765676487 # determined in create_model.py
