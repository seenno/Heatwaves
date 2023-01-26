'''
Heatwave detection in Estonian Environment Agency daily max temperature data.
Assumes the following columns: Aasta, Kuu, Paev, followed by any N of station columns.
Last edited: Sven-Erik Enno, 24/01/2023.
'''


import pandas as pd
import numpy as np



def test_year_stn(df_ys):
    '''
    Given an annual Pandas df, return heatwave stats.
    '''
    hd_idx = list(df_ys[df_ys >= 27].index)
    hws = []
    hw = []
    for day in hd_idx:
        if len(hw) == 0:
            hw.append(day)
        else:
            if (day - hw[-1] == 1):
                hw.append(day)
            elif (day - hw[-1] == 2):
                hw.append(day - 1)
                hw.append(day)
            else:
                hws.append(hw)
                hw = [day]
    hws.append(hw)
    durations = [len(hw) for hw in hws]
    n_days = sum(durations)
    durations_hws = [d for d in durations if d >= 3]
    n_hws = len(durations_hws)
    max_dur = max(durations)
    n_days_hw = sum(durations_hws)
    
    return n_days, n_hws, max_dur, n_days_hw


def process_file(data_file):
    '''
    Given an input xlsx file, iterate over years and stations and
    output heatwave stats.
    '''
    df = pd.read_excel(data_file)
    years = df["Aasta"].unique()
    stations = list(df.columns)[3:]
    days, hws, durations, days_hws = {}, {}, {}, {}
    for year in years:
        df_y = df[df['Aasta'] == year]
        days_y, hws_y, durations_y, days_hws_y = {}, {}, {}, {}
        for stn in stations:
            df_ys = df_y[stn]
            n_days, n_hws, max_dur, n_days_hw = test_year_stn(df_ys)
            days_y[stn] = n_days
            hws_y[stn] = n_hws
            durations_y[stn] = max_dur
            days_hws_y[stn] = n_days_hw
        days[year] = days_y
        hws[year] = hws_y
        durations[year] = durations_y
        days_hws[year] = days_hws_y
        
    days = pd.DataFrame(days).transpose()
    hws = pd.DataFrame(hws).transpose()
    durations = pd.DataFrame(durations).transpose()
    days_hws = pd.DataFrame(days_hws).transpose()
    
    return days, hws, durations, days_hws
    



def Main():
    # Input file path here, ./ means this directory.
    data_file = './Kuumalained.xlsx'
    
    # Compute heatwave stats.
    days, hws, durations, days_hws = process_file(data_file)
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('./Heatwaves_stats.xlsx', engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    days.to_excel(writer, sheet_name='N_days')
    hws.to_excel(writer, sheet_name='N_waves')
    durations.to_excel(writer, sheet_name='Max_duration')
    days_hws.to_excel(writer, sheet_name='N_days_hwaves')

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
    
    print(f'FINISHED! Output data written to ./Heatwaves_stats.xlsx.')

    

if  __name__ == '__main__':
    Main()

