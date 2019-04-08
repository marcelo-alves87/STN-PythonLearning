import xlsxwriter
import csv
import os
import string

def print_header(worksheet):
    worksheet.write(0, 0, 'Freq')
    
def input_file_csv(worksheet,index,group,c,param_to_read,value2,groupname):
    if group[-3] == '-':
        filename = group[:-3] + c + group[-3:]
    else:
        filename = group + c
             
    worksheet.write(0, index + 1, c)
    freq = []
    value = []
    param = 0
    with open(groupname + '/' + group[2:] + '/' + filename + '.csv', 'r') as f:
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

def csv_to_xlsx_group(groupname,groupset):
    for group in groupset:
        workbook = xlsxwriter.Workbook(groupname + '/' + group + ".xlsx")

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

        letters = ['A','B','C','D','E'] 
        
        for i in range(len(letters)):
            input_file_csv(worksheet_s11,i,group,letters[i],0,1,groupname)
            input_file_csv(worksheet_phase,i,group,letters[i],1,1,groupname)   
            input_file_csv(worksheet_vswr,i,group,letters[i],2,1,groupname)
            input_file_csv(worksheet_real,i,group,letters[i],3,1,groupname)
            input_file_csv(worksheet_imag,i,group,letters[i],3,2,groupname)

        workbook.close()
             
def make_groups(folders):
    dict1 = {}
    for folder in folders:#Excel Name
        if os.path.isdir(folder):
             groups = []
             subfolders = os.listdir(folder)
             for subfolder in subfolders:
                files = os.listdir(folder+'/'+subfolder) 
                for file in files:
                    if file.find('.csv') > 0:
                        file = file.split('.csv')[0]
                        if len(file.split('-')) > 1:
                            group = file[:-4] + file[-3:]
                        else:
                            group = file[:-1]
                        if group not in groups:
                            groups.append(group)
             dict1[folder] = groups
    return dict1


    

folders = os.listdir()
keys = make_groups(folders)
for key in keys:
    csv_to_xlsx_group(key,keys[key])
