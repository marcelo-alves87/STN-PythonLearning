import visa
import time
# start of untitled

def ext_query_bin_data_to_file(device, query, pc_file_path):
    file_data = device.query_binary_values(query, datatype='s')[0]
    new_file = open(pc_file_path, "wb")
    new_file.write(file_data)
    new_file.close()

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

prompt = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (1))
input(prompt)
N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (1))
prompt1 = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (2))
input(prompt1)
N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (2))
prompt2 = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (3))
input(prompt2)
N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (3))
N9952A.write('*OPC')
time.sleep(3)

N9952A.write(':SENSe:CORRection:COLLect:SAVE %d' % (0))

N9952A.write(':DISPlay:WINDow:SPLit %s' % ('D1'))

N9952A.write(':CALCulate:SELected:FORMat %s' % ('PHASe'))
N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('Phase.csv'))
time.sleep(1)
ext_query_bin_data_to_file(N9952A,':MMEMory:DATA? "%s"' % ('Phase.csv'),'MyPhase.csv')
N9952A.write(':MMEMory:DELete "%s"' % ('Phase.csv'))

N9952A.write(':CALCulate:SELected:FORMat %s' % ('MLOGarithmic'))
N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('MLog.csv'))
time.sleep(1)
ext_query_bin_data_to_file(N9952A,':MMEMory:DATA? "%s"' % ('MLog.csv'),'MyMLog.csv')
N9952A.write(':MMEMory:DELete "%s"' % ('MLog.csv'))

N9952A.write(':CALCulate:SELected:FORMat %s' % ('SWR'))
N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('SWR.csv'))
time.sleep(1)
ext_query_bin_data_to_file(N9952A,':MMEMory:DATA? "%s"' % ('SWR.csv'),'MySWR.csv')
N9952A.write(':MMEMory:DELete "%s"' % ('SWR.csv'))


N9952A.write(':CALCulate:SELected:FORMat %s' % ('SMITh'))
N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('Smith.csv'))
time.sleep(1)
ext_query_bin_data_to_file(N9952A,':MMEMory:DATA? "%s"' % ('Smith.csv'),'MySmith.csv')
N9952A.write(':MMEMory:DELete "%s"' % ('Smith.csv'))

N9952A.close()
rm.close()

# end of untitled
