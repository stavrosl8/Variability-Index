import pandas as pd
import numpy as np
import tqdm

df = pd.read_csv('Data.csv', parse_dates=True , index_col='datetime')

def VI(GHI_data_i, GHI_data_i_plus_1):
     Length = float(GHI_data_i_plus_1) - float(GHI_data_i)
     Length = np.sqrt(Length**2 + 1) # 1 refers to ΔΤ = 1 min (time increment)
     return(Length)
 
def std(std_data, GHI_avg):
    sigma = 1/(GHI_avg * np.std(std_data))
    return(sigma)

def min_max(data_dif):
    max_dif = np.abs(data_dif).max()
    return(max_dif)

results = []

for date in tqdm.tqdm(df.index):
    
    x_test = df[date:date + pd.Timedelta(minutes=20)]
    
    if len(x_test) >= 10:
        initial_value = x_test.loc[[date]]
        minute_initial = initial_value.index.minute[0]
       
        L_minute_measured, L_minute_clear, std_minute_measured, std_minute_clear = [], [], [], []
        
        for minute in range(1, 20, 1):        
            if date + pd.Timedelta(minutes=minute)  in x_test.index:
                if date + pd.Timedelta(minutes=minute+1) in x_test.index:
                    GHI_i_measured = float(x_test['GHI_measured'].loc[[date + pd.Timedelta(minutes=minute)]])
                    GHI_i_plus_1_measured = float(x_test['GHI_measured'].loc[[date + pd.Timedelta(minutes=minute+1)]])
                    GHI_i_clear = float(x_test['GHI_clear'].loc[[date + pd.Timedelta(minutes=minute)]])
                    GHI_i_plus_1_clear = float(x_test['GHI_clear'].loc[[date + pd.Timedelta(minutes=minute+1)]])
                                
                    L_minute_measured.append(VI(GHI_i_measured, GHI_i_plus_1_measured)) 
                    L_minute_clear.append(VI(GHI_i_clear, GHI_i_plus_1_clear))
                    std_minute_measured.append(GHI_i_plus_1_measured - GHI_i_measured)
                    std_minute_clear.append(GHI_i_plus_1_clear - GHI_i_clear)
                    
                else:
                    print(date, minute)
                    pass
       
        sigma_clear = std(std_minute_clear, x_test['GHI_clear'][1:].mean())
        sigma_measured = std(std_minute_measured, x_test['GHI_measured'][1:].mean())
        L_measured_sum = sum(L_minute_measured)
        L_clear_sum = sum(L_minute_clear)
        min_max_clear = min_max(std_minute_clear)
        min_max_measured = min_max(std_minute_measured)
        
        dif_window = {'Forecating Starting Time UTC':str(date),
                      'std_clear': sigma_clear,'std_measured': sigma_measured,
                      'L_clear_sum': L_clear_sum,
                      'L_measured_sum': L_measured_sum,
                      'min_max_clear': min_max_clear,
                      'min_max_measured': min_max_measured}
        
        results.append(dif_window)        
      
df_results = pd.DataFrame(results)
df_results.to_csv('VI_data.csv', index=0)
