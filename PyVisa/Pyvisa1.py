import visa
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv

def input_file_csv(type1):
    xs, ys = normalize_csv(type1 + '.csv')
    plt.ylabel(type1)
    plt.plot(xs,ys)

def normalize_csv(filename):
    xs = []
    ys = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)

def plot():
    style.use('fivethirtyeight')
    input_file_csv('PHASe')
    plt.xlabel('Frequencies')
    plt.show()
    

def calibrate(device, scount):
    print('Iniciando a calibração ...')
    for i in range(scount):
        prompt = device.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (i + 1))
        input(prompt)
        device.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (i + 1))

    device.write('*OPC')
    time.sleep(3)
    device.write(':SENSe:CORRection:COLLect:SAVE %d' % (0))
    device.write(':DISPlay:WINDow:SPLit %s' % ('D1'))

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

def config(device):
    device.timeout = 5000
    b = write_command(device,':INSTrument:SELect "%s"' % ('NA')) and write_command(device,':SENSe:FREQuency:STOP %G' % (1000000000.0)) and write_command(device,':SENSe:FREQuency:STARt %G' % (2000000.0)) and write_command(device,':SENSe:SWEep:POINts %d' % (1001)) and write_command(device,':FORMat:DATA %s,%d' % ('REAL', 64)) and write_command(device,':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50')) and write_command(device, ':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F')) and write_command(device,':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1'))
    time.sleep(1)
    return b

def connect(resource):
    try:
        return rm.open_resource(resource)
    except visa.VisaIOError:
       return None
    

def concat_csv(st1):
    return st1 + '.csv'

def ext_query_bin_data_to_file(device, query, pc_file_path):
    file_data = device.query_binary_values(query, datatype='s')[0]
    new_file = open(pc_file_path, "wb")
    new_file.write(file_data)
    new_file.close()

def dump_csv_parameter(device, parameter):
    device.write(':CALCulate:SELected:FORMat %s' % parameter)
    device.write(':MMEMory:STORe:FDATa "%s"' % concat_csv(parameter))
    time.sleep(1)
    ext_query_bin_data_to_file(device,':MMEMory:DATA? "%s"' % concat_csv(parameter),concat_csv(parameter))
    device.write(':MMEMory:DELete "%s"' % concat_csv(parameter))

 
rm = visa.ResourceManager()

device = connect('TCPIP0::192.168.0.173::inst0::INSTR')
if(device != None):
    config(device)
    temp_values = device.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
    scount = int(temp_values[0])
    
    if(scount > 0):
       # calibrate(device)
        input('Pluge o cabo na haste de âncora')
        dump_csv_parameter(device, 'PHASe')
        dump_csv_parameter(device, 'MLOGarithmic')
        dump_csv_parameter(device, 'SWR')
       # dump_csv_parameter(device, 'SMITh')
        
        plot()
        
    else:
        print('Houve um erro na configuração do instrumento. Por favor, tente novamente!')
    device.close()
else:
    print('Não foi possível realizar a conexão com o intrumento!')    
rm.close()

# end of untitled
