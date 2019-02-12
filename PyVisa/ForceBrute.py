import visa
import time
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

style.use('seaborn-darkgrid')

def input_file_csv(type1,plot=False):
    xs, ys = normalize_csv(type1 + '.csv')

    if plot:
        plt.plot(xs,ys, label=type1)
        plt.legend()
        plt.gca().invert_yaxis()
        plt.show()

    return xs, ys

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
               #1 STF 
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
    device.write(':MMEMory:STORe:FDATa "%s"' % concat_csv(parameter))
    device.write('*OPC')
    time.sleep(1)
    device.write('*OPC')
    
    ext_query_bin_data_to_file(device,':MMEMory:DATA? "%s"' % concat_csv(parameter),concat_csv(parameter))
    time.sleep(1)
    
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

def config(device,min_input_distance,max_input_distance):
    device.timeout = 5000
    device.read_termination = '\r'
    b = write_command(device,':INSTrument:SELect "%s"' % ('CAT')) and write_command(device,':CALCulate:SELected:TRANsform:DISTance:STARt %G' % min_input_distance) and write_command(device,':CALCulate:SELected:TRANsform:DISTance:STOP %G' % max_input_distance) and write_command(device,':CALCulate:SELected:TRANsform:DISTance:UNIT %s' % ('METers')) and write_command(device,':FORMat:DATA %s,%d' % ('REAL', 64)) and write_command(device,':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50')) and write_command(device, ':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F')) and write_command(device,':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1')) and write_command(device,':CALCulate:PARameter:DEFine %s' % ('DTF1'))
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

input_distance=2
fv=0
resolution=0.01
rm = visa.ResourceManager()
device = rm.open_resource('TCPIP0::192.168.0.173::inst0::INSTR')

if(device != None and config(device,1,2)):
    temp_values = device.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
    scount = int(temp_values[0])
    if(scount >= 0):
        #calibrate(device, scount)
        #input('Pluge o cabo na haste de ancora')
        diff = 1
##        while round(abs(diff),2) > resolution:
##            write_command(device, ':SENSe:CORRection:RVELocity:COAX %G' % (fv))
##            dump_csv_parameter(device, 'DTF')
##            x,y = input_file_csv('DTF')
##            sort = sorted(y)
##            sort_y = np.where(y == sort[0])
##            print(x[sort_y][0], sort[0])
##            diff = input_distance - x[sort_y][0]
##            print(diff)
##            print("Fator de velocidade:",fv,"Comprimento",x[sort_y][0])
##            fv=fv+resolution
        dump_csv_parameter(device, 'DTF')
        input_file_csv('DTF', True)  
    else:
        print('Houve um erro na configuracao do instrumento. Por favor, tente novamente!')
    device.close()
else:
    print('Nao foi possivel realizar a conexao com o intrumento!')      
rm.close()    

# end of untitled
