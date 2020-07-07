import visa
import time



rm = visa.ResourceManager()
device = rm.open_resource('TCPIP0::192.168.0.174::inst0::INSTR')

print(device.query('SYST:BATT:ABSC?'))


device.close() 
rm.close()    

