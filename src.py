import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


'''
Creates the appropriate title for each heatmap output from the Random Forest Regressor
'''
def get_title(name):
    for short, long in dict({'Mon':'Monday', 'Tue':'Tuesday', 'Wed':'Wednesday', 'Thu':'Thursday', 
                         'Fri':'Friday', 'Sat':'Saturday', 'Sun':'Sunday'}).items():
        name=name.replace(short, long)
    day=name.split(' ')[0]
    shift=name.split(' ')[1]
    shift_start=shift.split('-')[0]
    shift_end=shift.split('-')[1]
    shift_end=shift_end[0:len(shift_end)-1]
    return 'Crime normalised frequency distribution on a typical '+ day + ' between ' + shift_start + 'h and ' + shift_end + 'h'

'''
Formats a shp file into a pandas DataFrame
'''
def shp_to_df(sf):
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    df.drop(columns=['TOOLTIP'], inplace=True)
    return df

'''
Plots the map of LA
- crime mode: one dot per crime in history
- heatmap mode: fills a colored grid, colors scaled to the data input values, and adds it over the district boundaries map
'''
def plot_map_LA(sf, nb_vertical, nb_horizontal, crimes=True, heatmap = False, save_map=False, data_count=None, map_title=None):
    if(crimes):
         figsize = (11,16)
    if(heatmap):
        figsize = (11,13)
    '''
    Plot map with lim coordinates
    '''
    min_lat = 33.703656
    max_lat = 34.342
    min_long = -118.6682
    max_long = -118.1468
    
    plt.figure(figsize = figsize)
    plt.grid(False)
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, 'k', linewidth=0.3)
        x0 = np.mean(x)
        y0 = np.mean(y)
    
    long_range = np.arange(min_long, max_long, 0.01086)
    lat_range = np.arange(min_lat, max_lat, 0.00899)
    
    # plot grid
    for i, lon in enumerate(long_range):  
        plt.plot([lon, lon], [min_lat, max_lat], color="skyblue", linewidth=0.2, alpha = 0.9)
        plt.ylabel('Longitude (in degrees)')
        if (i!=48): plt.text(lon+0.001, min_lat-0.0091, i+1, fontsize=8)
    for i, lat in enumerate(lat_range):  
        plt.plot([min_long, max_long], [lat, lat], color="skyblue", linewidth=0.2, alpha = 0.9)
        plt.xlabel('Latitude (in degrees)')
        if (i!=71): plt.text(min_long-0.0194, lat+0.001, i+1, fontsize=8)
    
    # plot crimes
    if(crimes):
        lat = data['Latitude'].to_list()
        long = data['Longitude'].to_list()
        plt.scatter(np.array(long), np.array(lat), c='r', alpha=0.2, s=0.2)
    
    #plot heatmap
    if(heatmap):
        long_centers = [(long_range[i]+long_range[i+1])/2.0 for i in range(len(long_range)) if i<len(long_range)-1]
        lat_centers = [(lat_range[i]+lat_range[i+1])/2.0 for i in range(len(lat_range)) if i<len(lat_range)-1]
        data_q_viz = pd.DataFrame({'Cell Nb': np.arange(nb_vertical*nb_horizontal)+1})
        data_q_viz['Row Nb'] = np.mgrid[1:nb_vertical+1,1:nb_horizontal+1][0].flatten()
        data_q_viz['Col Nb'] = np.mgrid[1:nb_vertical+1,1:nb_horizontal+1][1].flatten()
        data_q_viz['Cell Long'] = data_q_viz['Col Nb'].apply(lambda col: long_centers[col-1])
        data_q_viz['Cell Lat'] = data_q_viz['Row Nb'].apply(lambda row: lat_centers[row-1])
        
        observation = pd.DataFrame(data_count).reset_index()
        observation.columns=['Cell Nb', 'Observation']
    
        data_q_obs = np.empty(nb_vertical*nb_horizontal)
        data_q_obs[:] = np.NaN

        for i in range(len(observation)):
            row = observation.iloc[i]
            data_q_obs[int(row['Cell Nb']-1)] = row['Observation']
        data_q_viz['Observations'] = data_q_obs

        x = data_q_viz['Cell Long']
        y = data_q_viz['Cell Lat']
        t = data_q_viz['Observations']
        nb_color = 15
        plt.scatter(x, y, c=t, cmap=cm.get_cmap('hot_r', nb_color), marker='s', s=60, vmin=0, vmax=1)
        plt.title(map_title)
        cbar = plt.colorbar()
        cbar.set_ticks(np.linspace(0, 1, nb_color+1))
    if(save_map):
        plt.savefig(map_title + '.png')
    plt.show()