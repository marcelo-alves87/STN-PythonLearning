import requests

rasp_ip = '177.58.246.103'

file_url = "http://{}/Measures/{}.csv"

files = ['MLOGarithmic', 'PHASe', 'SWR', 'SMITh'] 

for i in range(len(files)):
    
    r = requests.get(file_url.format(rasp_ip, files[i]))

    if r.status_code == 200:
        with open(files[i] + '.csv','wb') as f: 
           f.write(r.content) 
