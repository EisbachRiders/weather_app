import pandas as pd

# Import Eisbach temperature
# from data (baseline data München Himmelreichbrücke / Eisbach downloaded from
# https://www.gkd.bayern.de/de/fluesse/wassertemperatur/kelheim/muenchen-himmelreichbruecke-16515005/messwerte
# Format of numbers has been externally edited (e.g. 10,1 -> 10.1)
df_eis = pd.read_csv('./data/Eisbach_Temp.csv', sep=';')

# Import weather data from station München/Flughafen
# downloaded from
# https://www.dwd.de/DE/leistungen/klimadatendeutschland/klarchivtagmonat.html
df_temp = pd.read_csv('./data/produkt_klima_tag_19920517_20181231_01262.txt', sep=';', index_col='MESS_DATUM')

# ######## Prepare Data Frame of Eisbach Temperature for merging data frames #############
# Change date-format to match with df_temp
df_eis['MESS_DATUM'] = df_eis['Date'].apply(lambda x: ''.join(x.split('.')[::-1]))
df_eis.drop('Date',  axis=1, inplace=True)

# Change format of defined columns to float
df_eis['MESS_DATUM'] = df_eis['MESS_DATUM'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
df_eis['Max'] = df_eis['Max'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
df_eis['Min'] = df_eis['Min'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
# set new col as index
df_eis.set_index('MESS_DATUM', inplace=True)

# Merge both data frames
df = pd.merge(df_temp,df_eis, on='MESS_DATUM')

# Save merged data frame
df.to_csv('./data/data_combined.csv')
