#%%
"""
This code caluculate rain rate (mm/h) using dual-pol parameters
Input data must be radar object produced by pyart
"""
#%%

def R_Z(radar,mode='qc',a=32.5,b=1.65):
    """
    calc rain using Z-R relationship
    Z = a * R** b
    """
    
    ### check if data qc done
    if 'cor_Zh' in radar.fields.keys()== False:
        print('Please finish data QC by "data_qc4qpe" befor caluclation!')
        print('Now raw data are used...')
        mode == 'raw'
    
    if mode =='raw':
        Zhh = radar.fields['reflectivity']['data']
    else: 
        Zhh = radar.fields['cor_Zh']['data']
        
    Z = 10**(Zhh/10) 
    R = (Z/a)**(1/b)
    dict = {'data': R, 'units': 'mm/h', 'long_name': 'rainfall_rate_by_Z-R',
    '_FillValue': 'nan', 'standard_name': 'R_Z'}
    radar.add_field('rr_zh',dict,replace_existing=True)
    return radar

def R_Z_Zdr(radar,mode='qc'):
    """
    R(Z,Zdr)
    
    """ 
    ### check if data qc done
    if 'cor_Zh' in radar.fields.keys()== False:
        print('Please finish data QC by "data_qc4qpe" befor caluclation!')
        print('Now raw data are used...')
        mode == 'raw'
        
    if mode =='raw':
        Zhh = radar.fields['reflectivity']['data']
        Zdr = radar.fields['differential_reflectivity']['data']
    else: 
        Zhh = radar.fields['cor_Zh']['data']
        Zdr = radar.fields['cor_Zdr']['data']
    
    Z = 10**(Zhh/10) 
    R = 0.0067*Z**0.93*10**(0.1*(-3.43)*Zdr)
    dict = {'data': R, 'units': 'mm/h', 'long_name': 'rainfall_rate',
    '_FillValue': 'nan', 'standard_name': 'R_Z-Zdr'}
    radar.add_field('rr_zh_zdr',dict,replace_existing=True)
    return radar


def R_Kdp(radar,mode='qc'):
    """
    R(Kdp)
    
    """ 
    ### R(Kdp)
    Kdp = radar.fields['specific_differential_phase']['data']
    R = 50.7*Kdp**0.85
    dict = {'data': R, 'units': 'mm/h', 'long_name': 'rainfall_rate',
    '_FillValue': 'nan', 'standard_name': 'R_Kdp'}
    radar.add_field('rr_kdp',dict,replace_existing=True)
    return radar


def R_Kdp_Zdr(radar,mode='qc'):
    """
    R(Kdp,Zdr)
    
    """ 
    ### check if data qc done
    if 'cor_Zh' in radar.fields.keys()== False:
        print('Please finish data QC by "data_qc4qpe" befor caluclation!')
        print('Now raw data are used...')
        mode == 'raw'
        
    if mode =='raw':
        Zdr = radar.fields['differential_reflectivity']['data']
    else: 
        Zdr = radar.fields['cor_Zdr']['data']
        
    Kdp = radar.fields['specific_differential_phase']['data']
    
    ### R(Kdp,Zdr)
    R = 90.8*Kdp**0.93*10**(0.1*(-1.69)*Zdr)
    dict = {'data': R, 'units': 'mm/h', 'long_name': 'rainfall_rate',
    '_FillValue': 'nan', 'standard_name': 'R_Kdp-Zdr'}
    radar.add_field('rr_kdp_zdr',dict,replace_existing=True)
    return radar


def get_all_QPE(radar):
    radar = R_Z(radar)
    radar = R_Z_Zdr(radar)
    radar = R_Kdp(radar)
    radar = R_Kdp_Zdr(radar)
    return radar
 
