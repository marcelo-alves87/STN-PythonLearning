import visa
import time
# start of untitled

rm = visa.ResourceManager()
N9952A = rm.open_resource('TCPIP0::A-N9923A-91501::inst0::INSTR')
idn = N9952A.query('*IDN?')
print(idn)
##N9952A.timeout = 5000
##N9952A.write(':INSTrument:SELect "%s"' % ('NA'))
##N9952A.write(':SENSe:FREQuency:STOP %G' % (1000000000.0))
##N9952A.write(':SENSe:FREQuency:STARt %G' % (2000000.0))
##N9952A.write(':SENSe:SWEep:POINts %d' % (1001))
##N9952A.write(':SENSe:CORRection:COLLect:CONNector %d,"%s"' % (1, 'Type-N -F-,50'))
##N9952A.write(':SENSe:CORRection:COLLect:CKIT:LABel %d,"%s"' % (1, '85032F'))
##N9952A.write(':SENSe:CORRection:COLLect:METHod:SOLT1 %s' % ('1'))
##temp_values = N9952A.query_ascii_values(':SENSe:CORRection:COLLect:GUIDed:SCOunt?')
##scount = int(temp_values[0])
##
##prompt = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (1))
##N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (1))
##prompt1 = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (2))
##N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (2))
##prompt2 = N9952A.query(':SENSe:CORRection:COLLect:GUIDed:STEP:PROMpt? %d' % (3))
##N9952A.write(':SENSe:CORRection:COLLect:GUIDed:STEP:ACQuire %d' % (3))
##N9952A.write('*OPC')
##N9952A.write(':SENSe:CORRection:COLLect:SAVE %d' % (0))
##N9952A.write(':DISPlay:WINDow:SPLit %s' % ('D1'))
##N9952A.write(':CALCulate:SELected:FORMat %s' % ('PHASe'))
##N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('Phase.csv'))
##N9952A.write(':CALCulate:SELected:FORMat %s' % ('MLOGarithmic'))
##N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('MLog.csv'))
##N9952A.write(':CALCulate:SELected:FORMat %s' % ('SWR'))
##N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('SWR'))
##N9952A.write(':CALCulate:SELected:FORMat %s' % ('SMITh'))
##N9952A.write(':MMEMory:STORe:FDATa "%s"' % ('Smith.csv'))
##N9952A.write('*OPC')
N9952A.close()
rm.close()

# end of untitled
