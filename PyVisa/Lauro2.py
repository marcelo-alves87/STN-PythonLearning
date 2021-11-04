import visa
import time



rm = visa.ResourceManager()
device = rm.open_resource('TCPIP0::192.168.1.111::inst0::INSTR')

device.write(':INITiate:CONTinuous %d' % (1))
device.write('*OPC')


device.close() 
rm.close()    

