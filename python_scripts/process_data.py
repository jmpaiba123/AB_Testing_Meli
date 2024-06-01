# Preparamos el entorno
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import sys
import os

module_path = os.path.abspath(os.path.join('/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/', 'python_scripts'))
if module_path not in sys.path:
    sys.path.append(module_path)
from utilities import AnalisisExperimento # type: ignore

df = pd.read_csv('/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/data/Inputs/Experiments DataSet For Excercise-small.csv', sep=",")
df["datetime"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%z")
df["date"] = pd.to_datetime(df["datetime"]).dt.date

print("")
print("Registros por fecha: ")
print(df.date.value_counts().sort_index())
print("")
print("Usuarios unicos por fecha: " + str(df.groupby('date')['user_id'].nunique()))
print("")
print("Cantidad de registros :" + str(df.shape))
print("Cantidad de usuarios únicos :" + str(df.user_id.nunique()))
print("Cantidad de items únicos :" + str(df.item_id.nunique()))
print("")
print("Secciones del sitio navegadas: ")
print(df.event_name.value_counts())
print(df.site.value_counts())

compras = df[df['event_name'] == 'BUY'][['item_id', 'user_id']].drop_duplicates()
dupla_compra = set(tuple(x) for x in compras.values)

# funcion para determinar si un registro se encuentra en la cadena de compra
def in_purchase_funnel(row):
    if pd.notna(row['item_id']):  # Only consider rows with a valid item_id
        return 1 if (row['item_id'], row['user_id']) in dupla_compra else 0
    return 0

# aplicamos la funcion a nuestro df, e insertamos el fla en una nueva columna
df['purchase_funnel_flag'] = df.apply(in_purchase_funnel, axis=1)

# organización del dataframe por usuario e item 
df_sorted = df.sort_values(by=['user_id', 'datetime']).reset_index(drop=True)
# vector booleano que contiene navegaciones actuales de éxito
mask = df_sorted['purchase_funnel_flag'] == 1

# creación de columnas, con data de las nvegaciones inmediatamente anteriores
df_sorted['prev_event'] = df_sorted['event_name'].shift(1)
df_sorted['prev_user'] = df_sorted['user_id'].shift(1).fillna(0).astype(int)
df_sorted['prev_date'] = df_sorted['date'].shift(1)

# marcamos ahora eventos anteriores que sean de búsqueda, de un mismo usuario, de una misma fecha y que su valor en la cadena de compra sea positivo
search_mask = (df_sorted['prev_event'] == 'SEARCH') & (df_sorted['user_id'] == df_sorted['prev_user']) & (df_sorted['date'] == df_sorted['prev_date']) & (df_sorted['purchase_funnel_flag'] == 1)
search_mask_1 = search_mask.shift(-1)

# Update purchase_funnel_flag where mask is True and search_mask is True
df_sorted.loc[mask | search_mask_1, 'purchase_funnel_flag'] = 1

# Eliminamos las columnas recientemente creadas
df_sorted.drop(columns=['prev_event','prev_user','prev_date'], inplace=True)

# Apply the function to the 'experiments' column and create a new column with the dictionaries
df_sorted['experiments_dict'] = df_sorted['experiments'].apply(AnalisisExperimento.str_to_dict)

print(df_sorted.purchase_funnel_flag.value_counts())

# aplicamos funcion explode_dict para apertura de diccionarios (funcion creada y documentada en python_scripts/utilities)
df_exploded = df_sorted.apply(AnalisisExperimento.explode_dict, axis=1).reset_index(drop=True)
df_exploded = pd.concat(df_exploded.to_list(), ignore_index=True)
df_exploded.drop(columns=['experiments_dict','timestamp','experiments'], inplace=True)

# separamos columna experiment, para obtener su correspondiente descripción y variante
df_exploded[['path', 'experiment']] = df_exploded['experiment_key'].str.split('/', expand=True)
df_exploded.rename(columns={'experiment_value': 'variant'}, inplace=True)

# Agrupamos con variables necesarias para conteo, asignacion de 0's a registros con item_id nulo
df_exploded['item_id'] = df_exploded['item_id'].fillna(0)
df_grouped = df_exploded.groupby(['date','experiment','variant','user_id','path']).agg({'purchase_funnel_flag': 'max',  'item_id': lambda x: x[df_exploded['purchase_funnel_flag'] != 0].nunique()}).reset_index()

df_grouped_00 = df_grouped.groupby(['date', 'experiment', 'variant']).agg({'user_id': 'count', 'purchase_funnel_flag': 'sum'}).reset_index()
df_grouped_00 = df_grouped_00.rename(columns={"user_id": "participants" , "purchase_funnel_flag": "purchases"})
df_grouped_00['buy_rate'] = df_grouped_00 ['purchases']/df_grouped_00 ['participants']
df_grouped_00['buy_rate_percent'] = df_grouped_00['buy_rate'] .apply(lambda x: '{:.2f}%'.format(x*100))

# Cantidad única de experimentos 
unique_experiments = df_grouped_00["experiment"].nunique()
print(f"Cantidad única de experimentos : {unique_experiments}\n")

# cantidad única de experimentos por día
experiments_per_day = df_grouped_00.groupby("date")["experiment"].nunique().reset_index()
print("Cantidad única de experimentos por día:")
print(experiments_per_day.to_string(index=False))

df_grouped.to_csv('/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/data/Outputs/data_test.csv', sep = ",", index = False)
df_grouped_00.to_csv('/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/python_scripts/grouped_inf.csv', sep = ",", index = False)
df_grouped_00.to_csv('/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/data/Outputs/grouped_inf.csv', sep = ",", index = False)