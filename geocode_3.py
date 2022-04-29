import argparse
parser = argparse.ArgumentParser(description='Таблица для геокодирования')
parser.add_argument('indir', type=str, help='Путь к таблице')
parser.add_argument('outdir', type=str, help='Путь к папке где сохранить файл')
args = parser.parse_args()
print(args.indir)

from rtree.index import rtree
from geopandas.tools import geocode
from geopy.geocoders import Nominatim
import pandas as pd
import geopandas as gpd
import geopy
import os

data = pd.ExcelFile(r"args.indir")
df = pd.read_excel(data)

# датафрэйм с нулевыми координатами
new_df = df[df['Y_LAT'].isnull()]

# геокодировали адреса, там где нулевые координаты
locator = Nominatim(user_agent="my_request")
geocode = locator.geocode
new_df['location'] = new_df['address'].apply(geocode)
new_df['point'] = new_df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
del new_df['Y_LAT']
del new_df['X_LON']
new_df = new_df.dropna()
new_df[['Y_LAT_x', 'X_LON_x', 'altitude']] = pd.DataFrame(new_df['point'].tolist(), index=df.index)
df = df.merge(new_df, on='name', how='left')
df['Y_LAT'] = df['Y_LAT'].fillna(df['Y_LAT_x']) 
df['X_LON'] = df['X_LON'].fillna(df['X_LON_x'])

#сделали геодатафрэйм
new_gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=gpd.points_from_xy(df.X_LON, df.Y_LAT))

#добавили файлик для задания региона 
russia = gpd.read_file(r'adress.shp')
russia_new = russia[['geometry', 'name']].to_crs('epsg:4326')

#содеинили 
adress = gpd.sjoin(new_gdf, russia_new)
adress = adress[['objecttype_x','Y_LAT','X_LON','name_left','storyes_x','material_x','address_x','name_right']]
os.path.join(args.outdir, "adress.shp")
adress.to_file(os.path.join(args.outdir, "adress.shp"))