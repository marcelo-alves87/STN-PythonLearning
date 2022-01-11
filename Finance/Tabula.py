import tabula
import pandas as pd
#Leitor de PDF da RICO
file1 = "NOTA_DE_CORRETAGEM_10_01_2022.pdf"

df = pd.DataFrame(columns=['Ticker' , 'C/V', 'Qt.', 'Price', 'Value'])
for i in range(1,7):
    table = tabula.read_pdf(file1, pages=i)
    table = table[-1]
  
    for i,row in enumerate(table['Unnamed: 1']):
        if i > 7:
            df = df.append({'Ticker': row.split(' ')[1], 'C/V': table['Unnamed: 0'][i], 'Qt.': float(table['Unnamed: 4'][i].split(' ')[0].replace('.','')), 'Price': float(table['Unnamed: 4'][i].split(' ')[1].replace(',','.'))}, ignore_index = True)
            
for i in df.index:
    df['Value'][i] = df['Qt.'][i] * df['Price'][i]
    
#print(df.to_string())


df1 = df.groupby(['Ticker', 'C/V'], as_index=False)['Qt.', 'Value'].sum()
df2 = df.groupby(['Ticker', 'C/V'], as_index=False)['Price'].mean()
print(df2.merge(df1))
