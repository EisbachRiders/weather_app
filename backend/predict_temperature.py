import numpy as np

def predict_temperature(date, perception_level, sunshine, min_temp_outside, max_temp_outside):
    """
    function predict_temperature(year, month, rain, sunshine, min_temp, max_temp)
    returns maximum forcast temperature of Eisbach for the following input parameters

    year = current year
    month = current month as numeric
    perception_level = expected perception level for the day [mm]
    sunshine = Sunshine duration in [h]
    min_temp_outside = Minimum temperature in [°C]
    max_temp_outside = Maximum temperature in [°C]
    """
    # adapted input
    year  = int(date.split('.')[2])
    month = int(date.split('.')[1])
    input = np.array([year, month, perception_level, sunshine, min_temp_outside, max_temp_outside])
    coeff = np.array([0.06144129, 0.20976543, 0.02161775, 0.11419631, 0.33478473, 0.2672007]) # determined in create_model.py
    intercept = -119.94585765676487 # determined in create_model.py

    return coeff.dot(input)+intercept

print(predict_temperature("15.04.2020", 0, 12.2, -5, 14)) # taken data from meteomedia.de
