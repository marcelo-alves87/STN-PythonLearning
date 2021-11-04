import visa
import time
import sys


def ext_query_bin_data_to_file(device, query, pc_file_path):
    file_data = device.query_binary_values(query, datatype='s')[0]
    
    new_file = open(pc_file_path, "wb")
    new_file.write(file_data)
    new_file.close()

def concat_csv(st1):
    return st1 + '.csv'

def concat_png(st1):
    return st1 + '.png'


def dump(device, name):
    #device.write(':CALCulate:SELected:FORMat %s' % parameter)
    device.write(':MMEMory:STORe:FDATa "%s"' % concat_csv(name))
    device.write('*OPC')
    time.sleep(3)
    device.write('*OPC')
    device.write(':MMEMory:STORe:IMAGe "%s"' % concat_png(name))
    device.write('*OPC')
    time.sleep(3)
    device.write('*OPC')
    
    #ext_query_bin_data_to_file(device,':MMEMory:DATA? "%s"' % concat_csv(parameter),concat_csv(parameter))
    #time.sleep(10)
    
    #device.write('*OPC')
    #device.write(':MMEMory:DELete "%s"' % concat_csv(parameter))

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
    device.read_termination = '\r'
    b = write_command(device,':INSTrument:SELect "%s"' % ('NA')) and write_command(device,':SENSe:FREQuency:STOP %G' % (1000000000.0)) and write_command(device,':SENSe:FREQuency:STARt %G' % (2000000.0)) and write_command(device,':SENSe:SWEep:POINts %d' % (1001)) and write_command(device,':FORMat:DATA %s,%d' % ('REAL', 64)) and write_command(device,':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50')) and write_command(device, ':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F')) and write_command(device,':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1'))
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
device = rm.open_resource('TCPIP0::192.168.0.174::inst0::INSTR')
print(device)
##while amp <= 20:
##    device.write(':SENSe:CORRection:LOSS:COAX %s' % (amp))
##    dump(device, 'H2D140' + str(amp))
##    amp = amp + 0.5
##    print(amp)
##if(device != None and config(device)):
##    temp_values = device.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
##    scount = int(temp_values[0])
##    if(scount > 0):
##        #calibrate(device, scount)
##        input('Pluge o cabo na haste de ancora')
##        device.write(':DISPlay:WINDow:SPLit %s' % ('D1'))
##        dump_csv_parameter(device, 'PHASe')
##        dump_csv_parameter(device, 'MLOGarithmic')
##        dump_csv_parameter(device, 'SWR')
##        dump_csv_parameter(device, 'SMITh')
##    else:
##        print('Houve um erro na configuracao do instrumento. Por favor, tente novamente!')
##    device.close()
##else:
##    print('Nao foi possivel realizar a conexao com o intrumento!')      
rm.close()    

# end of untitled
