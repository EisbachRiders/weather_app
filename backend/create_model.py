import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.read_csv('./data/data_combined.csv')

#df colums description
# () data in brackets not taken for model
# (QN) = Qualitätsniveau der Daten (10=geprueft)
# (FM) = Mittel der Windstärke [m/s]
# (FX) = Maximum der Windgeschwindigkeit (Spitzenböe) [m/s]
# RSK = Niederschlagshöhe / Precipitation level [mm]
# (RSKF) = Kennung fuer die Art des Niederschlags
# SDK = Tagessumme der Sonnenscheindauer [h]
# (SHK_Tag) = Schneehoehe [cm]
# (NM) = Mittel des Bedeckungsgrades
# (VPM) = Tagesmittel des Dampfdrucks [hPa]
# (PM) = Tagesmittel des Luftdruckes in Stationshoehe [hPa]
# (TMK) = Tagesmittel der Temperatur der Luft in 2m Hoehe [°C]
# (UPM) = Tagesmittel der relativen Feuchte [%]
# TXK = Tagesmaximum der Temperatur der Luft in 2m Hoehe [°C]
# TNK = Tagesminimum der Temperatur der Luft in 2m Hoehe  [°C]
# (TGK) = Tagesminimum der Temperatur der Luft am Erdboden [°C]
# (MeanTemp) = Mittlere Temperatur Eisbach / Average Esibach Temperature [°C]
# Max = Maximale Temperatur Eisbach / Maximum Temperature Eisbach [°C]
# (Min) = Minimale Temperatur Eisbach / Minimum Temperature Eisbacht [°C]

# create data frame with temperature of eisbach the day before
df['MeanTemp'] = df['MeanTemp'].apply(lambda x: float(x) if not x =='--' else float('nan'))
df_temp_yest = df[['MESS_DATUM', 'Max']]
df_temp_yest.rename(columns={'Max': 'Temp_yest'}, inplace=True)
df_temp_yest['MESS_DATUM'] = df_temp_yest['MESS_DATUM'].apply(lambda x: x + 1)

df.set_index('MESS_DATUM', inplace=True)
df_temp_yest.set_index('MESS_DATUM', inplace=True)

# Merge data with overall data frame
df = pd.concat([df, df_temp_yest], axis=1)
df.reset_index(inplace=True)

# Change  format of MESS_DATUM to datetime
df['MESS_DATUM'] = pd.to_datetime(df['MESS_DATUM'], format='%Y%m%d', errors='coerce')

# Extract only important parameters from data frame for model fitting (first approach)
df_red = df[['MESS_DATUM', '  FX',' RSK',' SDK','  NM', '  PM', ' TXK', ' TNK', 'Temp_yest', 'MeanTemp', 'Max', 'Min']]
# delete all NAN values
df_red.dropna(inplace=True)

# Extract additional parameters from date (also first approach)
df_red['Year'] = df_red['MESS_DATUM'].apply(lambda x: x.year) # global warming impact?
df_red['Month'] = df_red['MESS_DATUM'].apply(lambda x: x.month) # season impact

# ################## TRAIN MODEL ###########################
model_max=LinearRegression()
# Taking all data, no separation in train and test data
model_max.fit(df_red[['Year', 'Month', ' RSK',' SDK', ' TXK', ' TNK', 'Temp_yest']], df_red['Max'])

model_min=LinearRegression()
# Taking all data, no separation in train and test data
model_min.fit(df_red[['Year', 'Month', ' RSK',' SDK', ' TXK', ' TNK', 'Temp_yest']], df_red['Min'])

print('Coefficients Maximum Temperatures:')
print(model_max.coef_) # [0.06144129, 0.20976543, 0.02161775, 0.11419631, 0.33478473, 0.2672007]
print(model_max.intercept_) # -119.94585765676487
print('\nCoefficients Minimum Temperatures:')
print(model_min.coef_)
print(model_min.intercept_)

