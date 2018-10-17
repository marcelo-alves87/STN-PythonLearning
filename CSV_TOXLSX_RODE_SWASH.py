import xlsxwriter
import csv

def print_header(worksheet):
    worksheet.write(0, 0, 'Freq')
    
def input_file_csv(worksheet,filename, index):
    worksheet.write(0, index, filename)
    freq = []
    s11 = []
    phase = []
    with open(filename + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].find('#') < 0 and row[0].find('f') < 0:            
                freq.append(float(row[0] + '.' + row[1].split(';')[0]))
                s11.append(float(row[1].split(';')[1] + '.' + row[2].split(';')[0]))
                phase.append(float(row[2].split(';')[1] + '.' + row[3].split(';')[0]))
    for i in range(len(freq)):
         worksheet.write_number(i + 1, 0, freq[i])
         worksheet.write_number(i + 1, index, phase[i])
         
def input_files_csv(worksheet):
    for i in range(10):
        input_file_csv(worksheet,'MED_' + str(i), i + 1)

workbook = xlsxwriter.Workbook('Med_Phase.xlsx')
worksheet = workbook.add_worksheet()

print_header(worksheet)
input_files_csv(worksheet)

workbook.close()
