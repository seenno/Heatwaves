'''
Heatwave detection in Estonian Environment Agency daily max temperature data.
Assumes the following columns: Aasta, Kuu, Paev, followed by any N of station columns.
Note that heatwave is defined as >=3 consecutive days with daily max
    temperatur equal/exceeding the hw_th. Heatwave continues if there is only
    a single day below hw_th as long as the previous and next day meet 
    the hw_th.
Last edited: Sven-Erik Enno, 24/01/2023.
'''


import pandas as pd
import numpy as np



def year_stn_stats(df_ys, hw_th, hw_min_days):
    '''
    Given an input Pandas df with daily max temperatures of one station during
    one year, and a fixed or daily/station specific threshold, find all
    heatwaves for this station during this year and output their statistics. 
    Args:
      df_ys = Pandas df, daily maximum temperatures of one station during one year.
      hw_th = float/int fixed heatwave temperature threshold or Pandas df with daily
        thresholds for this station.
      hw_min_days = minimum duration to be a heatwave, otherwise just heat days.
    Returns:
      n_days = int total N of days per year exceeding hw_th.
      n_hws = int total N of heatwaves.
      max_dur = int max duration of heatwave.
      n_days_hw = int total N of days during heatwaves.
    '''
    
    hd_idx = list(df_ys[df_ys >= hw_th].index)
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
    durations_hws = [d for d in durations if d >= hw_min_days]
    n_hws = len(durations_hws)
    max_dur = max(durations)
    n_days_hw = sum(durations_hws)
    
    return n_days, n_hws, max_dur, n_days_hw


def process_df(df, hw_th):
    '''
    Given an input Pandas df with daily max temperatures of N stations over N
    years (can also be a shorter standard period like 1 April to 30 September
    for every year), and a fixed or daily/station specific threshold, find all
    heatwaves by station and year, and output their statistics. 
    Args:
      df = Pandas df, stations x dates, daily maximum temperatures.
      hw_th = float/int fixed heatwave temperature threshold or
              Pandas df stations x days with day/station specific thresholds
              (note - this can be one number for each day, no need to repeat
              e.g. 10 times when analyzing 10 years).
    Returns:
      days = Pandas df total N of days per year/station exceeding hw_th.
      hws = Pandas df total N of heatwaves per year/station.
      max_durs = Pandas df max duration of heatwaves per year/station.
      days_hws = Pandas df total N of days per year/station in heatwaves.
    '''
    
    # Minimum duration to be a heatwave, otherwise just heat days.
    # Defining here as this should always be 3. 
    hw_min_days = 3
    
    years = df["Aasta"].unique()
    stations = list(df.columns)[3:]
    days, hws, max_durs, days_hws = {}, {}, {}, {}
    for year in years:
        df_y = df[df['Aasta'] == year]
        days_y, hws_y, max_durs_y, days_hws_y = {}, {}, {}, {}
        for stn in stations:
            df_ys = df_y[stn]
            n_days, n_hws, max_dur, n_days_hw = year_stn_stats(df_ys, hw_th, hw_min_days)
            days_y[stn] = n_days
            hws_y[stn] = n_hws
            max_durs_y[stn] = max_dur
            days_hws_y[stn] = n_days_hw
        days[year] = days_y
        hws[year] = hws_y
        max_durs[year] = max_durs_y
        days_hws[year] = days_hws_y
        
    days = pd.DataFrame(days).transpose()
    hws = pd.DataFrame(hws).transpose()
    max_durs = pd.DataFrame(max_durs).transpose()
    max_durs[max_durs < hw_min_days] = 0
    days_hws = pd.DataFrame(days_hws).transpose()
    
    return days, hws, max_durs, days_hws


def output_writer(fname, days, hws, max_durs, days_hws):
    '''
    Write the results into an xlsx file, on four separate worksheets.
    Args:
      fname = full path of the output xlsx file.
      days, hws, max_durs, days_hws = Pandas dfs with heatwave stats as
        described in process_df() output.
    '''
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    days.to_excel(writer, sheet_name='N_days')
    hws.to_excel(writer, sheet_name='N_waves')
    max_durs.to_excel(writer, sheet_name='Max_duration')
    days_hws.to_excel(writer, sheet_name='N_days_hwaves')

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
    
    print(f'FINISHED! Output data written to {fname}.')
    

def input_reader(fname, ws_data_name=None, ws_th_name=None):
    '''
    Read the daily maximum temperatures and, if required, also the daily
    heatwave thresholds from an xlsx file.
    Args:
      fname = full path of the input xlsx file.
      ws_data_name = name of the worksheet containing max temperature data.
      ws_th_name = name of the worksheet containing heatwave threshold data.
    Returns:
      df_data = Pandas dataframe containing all max temperature data in the file.
      df_ths = Pandas dataframe containing all heatwave threshold data in the 
        file, None if no data/fixed threshold.
    '''
    
    if ws_data_name is None:
        return pd.read_excel(fname), None
    else:
        pass
    


def Main():
    hw_fixed_th = 30
    
    # Input file path here, ./ means this directory.
    data_file = './Kuumalained.xlsx'
    df_data, hw_th = input_reader(data_file, ws_data_name=None, ws_th_name=None)
    
    # Compute heatwave stats.
    if hw_th is None:
        hw_th = hw_fixed_th
    days, hws, max_durs, days_hws = process_df(df_data, hw_th)
    
    # Write the stats into an output file.
    out_fname = f'./Heatwave_stats_th{hw_th}.xlsx'
    output_writer(out_fname, days, hws, max_durs, days_hws)

    

if  __name__ == '__main__':
    Main()

