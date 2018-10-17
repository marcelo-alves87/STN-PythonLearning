import xlsxwriter
import csv

def print_header(worksheet):
    worksheet.write(0, 0, 'Freq')
    
def input_file_csv(worksheet,filename,index,is_to_read):
    worksheet.write(0, index - 10, filename)
    freq = []
    value = []
    param = 0
    with open(filename + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].find('!') < 0 and row[0].find('BEGIN') < 0:
                if row[0].find('END') >= 0:
                    param += 1
                elif param == is_to_read:
                    freq.append(row[0])
                    value.append(row[1])
    for i in range(len(freq)):
         worksheet.write(i + 1, 0, freq[i])
         worksheet.write(i + 1, index - 10, value[i])
         
def input_files_csv(worksheet):
    
    for i in range(10,20):
        input_file_csv(worksheet,'MED_' + str(i), i + 1,1)

workbook = xlsxwriter.Workbook('Med_Phase.xlsx')
worksheet = workbook.add_worksheet()

print_header(worksheet)
input_files_csv(worksheet)

workbook.close()
