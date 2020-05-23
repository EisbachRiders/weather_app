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

    # Model based on absolute values
    coeff_min = np.array([0.00671369,  0.05433055, -0.01699897, -0.0091107,   0.04654794,  0.04494732,
                          0.80392883])  # determined in create_model.py
    intercept_min = -13.801013453736768  # determined in create_model.py

    coeff_max = np.array([0.0037455,  0.02092407, -0.00372701, 0.04690195, 0.06081745, 0.03382019, 0.84128262]) # determined in create_model.py
    intercept_max = -7.175286431561844 + 0.4 # determined in create_model.py

    pred_min= (coeff_min.dot(input)+intercept_min)
    pred_max = (coeff_max.dot(input)+intercept_max)

    return (round(pred_min*2,0)*0.5, round(pred_max*2,0)*0.5)

