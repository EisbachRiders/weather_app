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

# Change  format of MESS_DATUM to datetime
df['MESS_DATUM'] = pd.to_datetime(df['MESS_DATUM'], format='%Y%m%d', errors='coerce')

# Extract only important parameters from data frame for model fitting (first approach)
df_red = df[['MESS_DATUM', '  FX',' RSK',' SDK','  NM', '  PM', ' TXK', ' TNK', 'MeanTemp', 'Max', 'Min']]
# delete all NAN values
df_red.dropna(inplace=True)

# Extract additional parameters from date (also first approach)
df_red['Year'] = df_red['MESS_DATUM'].apply(lambda x: x.year) # global warming impact?
df_red['Month'] = df_red['MESS_DATUM'].apply(lambda x: x.month) # season impact

# ################## TRAIN MODEL ###########################
model=LinearRegression()
# Taking all data, no separation in train and test data
model.fit(df_red[['Year', 'Month', ' RSK',' SDK', ' TXK', ' TNK']], df_red['Max'])

print(model.coef_) # [0.06144129, 0.20976543, 0.02161775, 0.11419631, 0.33478473, 0.2672007]
print(model.intercept_) # -119.94585765676487