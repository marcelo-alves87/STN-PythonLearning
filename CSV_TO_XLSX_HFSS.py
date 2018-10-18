import xlsxwriter
import csv

def print_header(worksheet):
    worksheet.write(0, 0, 'Freq')
    
def input_file_csv(worksheet,filename,index):
    worksheet.write(0, index, filename)
    freq = []
    value = []
    with open(filename + '.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0].find('Freq') < 0:
                    freq.append(float(row[0])*1000)
                    value.append(float(row[1]))
    for i in range(len(freq)):
         worksheet.write(i + 1, 0, freq[i])
         worksheet.write(i + 1, index, value[i])
         
def input_files_csv(worksheet):
    input_file_csv(worksheet,'H1D10',1)
    input_file_csv(worksheet,'H1D10D80',2)
    input_file_csv(worksheet,'H1D15',3)
    input_file_csv(worksheet,'H1D25',4)
    input_file_csv(worksheet,'H1D30-20',5)
    input_file_csv(worksheet,'H1D50-20',6)
    input_file_csv(worksheet,'H1D65',7)
    input_file_csv(worksheet,'H1D75',8)
    input_file_csv(worksheet,'H1D80',9)

workbook = xlsxwriter.Workbook('H1.xlsx')
worksheet = workbook.add_worksheet()

print_header(worksheet)
input_files_csv(worksheet)

workbook.close()
