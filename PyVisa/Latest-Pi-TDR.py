import visa
import time
import sys
import pickle
import numpy as np
from numpy.fft import ifft
import matplotlib.pyplot as plt

INPUT_WIDTH=0.9
C=3*10**8
START_NUMBER_OF_POINTS=201
RESOLUTION=0.01
PARAMETER='MLOGarithmic'

def distance_to_fault(type1):
    pickle_in = open(type1 +  '.pickle', 'rb')
    y_mlog = pickle.load(pickle_in)
    sort = sorted(y)
    return INPUT_WIDTH - sort[-1]

def read_input_file(type1):
    pickle_in = open(type1 +  '.pickle', 'rb')
    y_mlog = pickle.load(pickle_in)
    y_mlog_i = ifft(y_mlog)
    y = abs(y_mlog_i)
    if len(y) > 0:
        sort = sorted(y)    
        nanoseconds = 0
        i = 0
        while nanoseconds == 0 and i < len(y):
            if sort[-i] - sort[-i-1] < RESOLUTION:
                nanoseconds = x[np.where(y == sort[-i])]                
            else:    
                i+=1          
        return (INPUT_WIDTH/nanosecondse^9)/C    
    else:
        return 0
            
    max_y = sort[-4]
   
    
    vp = 0.9/(z*(10**-9))
    fv=vp/(3*(10**8))
    return fv

def input_file_csv(type1,plot=False):
    xs, ys = normalize_csv(type1 + '.csv')

    with open(type1 + '.pickle', 'wb') as f:
        pickle.dump(ys,f)

    if plot:
        plt.plot(xs,ys, label=type1)
        
def normalize_csv(filename):
    xs = []
    ys = []
    end_index = 0
    
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if s.find('END') >= 0:
               end_index += 1 
               #1 S11, 2 Phase, 3 SWR, 4 Real/Imaginary 
               if end_index == 1: 
                   break
               else:
                   xs = []
                   ys = []               
            elif(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                if len(row) > 2:
                    #1 Real, 2 Imaginary
                    ys.append(row[1])
                else:
                    ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)        

def ext_query_bin_data_to_file(device, query, pc_file_path):
    file_data = device.query_binary_values(query, datatype='s')[0]
    
    new_file = open(pc_file_path, "wb")
    new_file.write(file_data)
    new_file.close()

def concat_csv(st1):
    return st1 + '.csv'

def dump_csv_parameter(device, parameter):
    device.write(':CALCulate:SELected:FORMat %s' % parameter)
    device.write(':MMEMory:STORe:FDATa "%s"' % concat_csv(parameter))
    device.write('*OPC')
    time.sleep(10)
    device.write('*OPC')
    
    ext_query_bin_data_to_file(device,':MMEMory:DATA? "%s"' % concat_csv(parameter),concat_csv(parameter))
    time.sleep(10)
    
    device.write('*OPC')
    device.write(':MMEMory:DELete "%s"' % concat_csv(parameter))

def write_command(device, command, retry=True):
    try:
       device.write(command)
       return True
    except visa.VisaIOError:
       if(retry): 
           time.sleep(1)
           device.write('*OPC')
           write_command(device, command, False)
       else: 
           return False

def config_number_of_points(number_of_points):
    write_command(device,':SENSe:SWEep:POINts %d' % number_of_points)

def config_start_stop_frequencies():
    write_command(device,':SENSe:FREQuency:STOP MAX')
    write_command(device,':SENSe:FREQuency:STARt MIN')
    
def config_device_mode(device_mode):
    write_command(device,':INSTrument:SELect "%s"' % device_mode)
    

def config(device):
    device.timeout = 5000
    device.read_termination = '\r'
    b =  write_command(device,':FORMat:DATA %s,%d' % ('REAL', 64)) and write_command(device,':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50')) and write_command(device, ':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F')) and write_command(device,':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1'))
    time.sleep(1)
    return b

def calibrate(device, scount):
    print('Iniciando a calibracao ...')
    for i in range(scount):
        prompt = device.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (i + 1))
        input(prompt)
        device.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (i + 1))

    device.write('*OPC')
    time.sleep(3)
    device.write(':SENSe:CORRection:COLLect:SAVE %d' % (0))
    device.write(':DISPlay:WINDow:SPLit %s' % ('D1'))

rm = visa.ResourceManager()
device = rm.open_resource('TCPIP0::192.168.0.173::inst0::INSTR')

if(device != None and config(device)):
    temp_values = device.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
    scount = int(temp_values[0])
    if(scount > 0):
        #calibrate(device, scount)
        
        diff = 0
        while diff == 0:
            config_device_mode('NA')
            config_start_stop_frequencies()
            
            dump_csv_parameter(device, PARAMETER)
            config_number_of_points(START_NUMBER_OF_POINTS + diff)
            input_file_csv(PARAMETER)
            fv = read_input_file(PARAMETER)
            if fv == 0:
                print('Não foi possível realizar a medição do estado da haste!')
                break
            else:
                config_device_mode('CAT')
                write_command(device,':SENSe:CORRection:RVELocity:COAX %d' % (fv))
                write_command(device,':CALCulate:SELected:TRANsform:DISTance:STARt MIN')
                write_command(device,':CALCulate:SELected:TRANsform:DISTance:STOP %d ' % (INPUT_WIDTH*1.5))
                     
                dump_csv_parameter(device, PARAMETER)
                diff = read_distance_to_fault(PARAMETER)
            
            input_file_csv(PARAMETER,True)
    else:
        print('Houve um erro na configuracao do instrumento. Por favor, tente novamente!')
    device.close()
else:
    print('Nao foi possivel realizar a conexao com o intrumento!')      
rm.close()    

# end of untitled
