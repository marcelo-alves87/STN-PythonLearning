import visa
import time
# start of untitled

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
    ext_query_bin_data_to_file(N9952A,':MMEMory:DATA? "%s"' % concat_csv(parameter),concat_csv(parameter))
    device.write(':MMEMory:DELete "%s"' % concat_csv(parameter))

 
rm = visa.ResourceManager()
N9952A = rm.open_resource('TCPIP0::192.168.0.173::inst0::INSTR')
idn = N9952A.query('*IDN?')
print(idn)
N9952A.timeout = 5000
N9952A.write(':INSTrument:SELect "%s"' % ('NA'))
N9952A.write(':SENSe:FREQuency:STOP %G' % (1000000000.0))
N9952A.write(':SENSe:FREQuency:STARt %G' % (2000000.0))
N9952A.write(':SENSe:SWEep:POINts %d' % (1001))
N9952A.write(':FORMat:DATA %s,%d' % ('REAL', 64))
N9952A.write(':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50'))
N9952A.write(':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F'))
N9952A.write(':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1'))
time.sleep(1)
temp_values = N9952A.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
scount = int(temp_values[0])

if(scount > 0):
    for i in range(scount):
        prompt = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (i + 1))
        input(prompt)
        N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (i + 1))
        
    N9952A.write('*OPC')
    time.sleep(3)
    
    N9952A.write(':SENSe:CORRection:COLLect:SAVE %d' % (0))
    
    N9952A.write(':DISPlay:WINDow:SPLit %s' % ('D1'))
    
    dump_csv_parameter(N9952A, 'PHASe')
    dump_csv_parameter(N9952A, 'MLOGarithmic')
    dump_csv_parameter(N9952A, 'SWR')
    dump_csv_parameter(N9952A, 'SMITh')

N9952A.close()
rm.close()

# end of untitled
