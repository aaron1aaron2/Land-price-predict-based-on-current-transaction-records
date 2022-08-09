"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.03
Last Update: 2022.08.03
Describe: 主辦單位的 54 個土地，作為我們的目標。透過地圖觀察在地理上的位置。
"""
import os
import pandas as pd

import folium
# from folium.features import DivIcon

output_folder = 'data/procces/supplementary'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result_mod.csv')
df.drop('result_text', axis=1, inplace=True)

m = folium.Map(
            [24.961640, 121.142500],
            zoom_start=12 )
# m = folium.Map(
#             [24.961640, 121.142500],
#             zoom_start=12,
#             tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga',
#             attr='Google') 

for i in df.to_dict(orient="records"):
    coordinate = [i['lat'], i['long']]

    popup = folium.Popup(str(pd.DataFrame([i]).T)[21:], max_width=300, min_width=300)

    # icon = folium.DivIcon(icon_size=(24, 30),
    #                         html=f"""<div style="font-family: courier new;
    #                             border-radius: 70%;
    #                             border: 1px solid #FFFFFF;
    #                             font-size: 12pt; color:{'white'}; 
    #                             text-align: center;
    #                             background-color: 'red'">O</div>""")

    folium.CircleMarker(location=coordinate,
                        radius=5, 
                        popup=popup,
                        color='red', 
                        fill=True,
                        fill_opacity=0.5).add_to(m)

    # folium.Marker(coordinate, popup=popup, icon=icon).add_to(m)

m.save(os.path.join(output_folder, "target_land_location_map.html"))