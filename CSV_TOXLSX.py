import xlsxwriter
import csv
import os
import string

def print_header(worksheet):
    worksheet.write(0, 0, 'Freq')
    
def input_file_csv(worksheet,index,group,c,param_to_read,value2=1):
    if group[-3] == '-':
        filename = group[:-3] + c + group[-3:]
    else:
        filename = group + c
             
    worksheet.write(0, index + 1, c)
    freq = []
    value = []
    param = 0
    with open(filename + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].find('!') < 0 and row[0].find('BEGIN') < 0:
                if row[0].find('END') >= 0:
                    param += 1
                elif param == param_to_read:
                    freq.append(float(row[0])/1000000)
                    value.append(row[value2])
    for i in range(len(freq)):
         worksheet.write(i + 1, 0, freq[i])
         worksheet.write(i + 1, index+1, value[i])

def csv_to_xlsx_group(group):
    workbook = xlsxwriter.Workbook(group + ".xlsx")

    worksheet_s11 = workbook.add_worksheet('S11')
    print_header(worksheet_s11)

    worksheet_phase = workbook.add_worksheet('PHase')
    print_header(worksheet_phase)
    
    worksheet_vswr = workbook.add_worksheet('VSWR')
    print_header(worksheet_vswr)

    worksheet_real = workbook.add_worksheet('Zin Real')
    print_header(worksheet_real)

    worksheet_imag = workbook.add_worksheet('Zin Imaginary')
    print_header(worksheet_imag)

    letters = ['A','B','C','D','E','F','G','H','I','J'] 
    
    for i in range(len(letters)):
       input_file_csv(worksheet_s11,i,group,letters[i],0)
       input_file_csv(worksheet_phase,i,group,letters[i],1)   
       input_file_csv(worksheet_vswr,i,group,letters[i],2)
       input_file_csv(worksheet_real,i,group,letters[i],3)
       input_file_csv(worksheet_imag,i,group,letters[i],3,2)

    workbook.close()
         
def make_groups(files):
    csvs = []
    for file in files:
        if file.find('.csv') > 0:
            file = file.split('.csv')[0]
            if len(file.split('-')) > 1:
                group = file[:-4] + file[-3:]
            else:
                group = file[:-1]
            if group not in csvs:    
                csvs.append(group)
    return csvs


    

files = os.listdir()
groups = make_groups(files)
for group in groups:
    csv_to_xlsx_group(group)

