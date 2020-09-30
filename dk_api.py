import os
import requests
import json 
import xlrd
import time


from zipfile import ZipFile


def get_api_bc(offset, count, codes):
    
    while True:
        try:
            response = requests.get(
    "https://kabinet.dreamkas.ru/api/products",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "isClosed": "true",
            },
            params={"limit": 1000,"offset": offset},
        )
            get_file = json.loads(response.text)
            json.dumps(get_file)
            for iter in range(1000):
                count += 1
                #with open("data_file.json", "w", encoding="utf-8") as write_file:
                    #json.dump(response.json(), write_file, indent=2, ensure_ascii=False)
                #print(count, [get_file[iter]['id']], get_file[iter]['name'], get_file[iter]['barcodes'])
                codes[str(get_file[iter]['barcodes'])] =  str([get_file[iter]['id']]).strip("[").strip("]").strip("'")
                print(str([get_file[iter]['id']]).strip("[").strip("]").strip("'"))
                #print(count, get_file[iter]['barcodes'], get_file[iter]['id'], get_file[iter]['tax'])
                       
            offset += 1000
        
        except PermissionError:
            break
  
        except IndexError:
            break
    return codes

def get_from_exel(codes ,token):
    i = 1
    while i != IndexError:
        try:
            read_file = xlrd.open_workbook("C:/Users/root/Desktop/dk_api/goods_standard.xlsx")
            sheet_num = read_file.sheet_by_index(0)
            barcode_value = int(sheet_num.row_values(i)[0])  
  
            if str(f"['{barcode_value}']") in codes:
                id = str(codes[str(f"['{barcode_value}']")]) # ['b1615355-efb3-431b-ba7a-084a3b27dc5c']
                print(id, str(f"['{barcode_value}']"), "True")
                response = requests.get(f"https://kabinet.dreamkas.ru/api/v2/products/{id}",
                                        headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}",
                                        "isClosed": "true",}) 
                print(response.text)
                i += 1
            else:
                print( str(f"['{barcode_value}']"), "False") 
                i += 1
        except IndexError:
            break
    #['4630015370841']
    #print(codes[str(f"[{barcode_value}]")], "true")
    
    #if str("['4601373005881']") in codes:
def get_from_price():
     
    file = open("C:/Users/root/Desktop/dk_api/БЖ300004.txt", "r")
    for line in file:  
        data = line.split('","')
        nom = str(data[1:2]).replace("['", '').replace("']", '')
        name = str(data[2:3]).replace("['", '').replace("']", '').replace("[\"", '').replace("\"]", '')
        group = str(data[4:5]).replace("['", '').replace("']", '').replace("1. ", '').capitalize()
        #group_id = str(data[5:6]).replace("['", '').replace(r"']", '')
        sub_group = str(data[6:7]).replace("['", '').replace("']", '')
        #print(nom, name, group + " - " + sub_group)
        data_c = str(data[3:4]).split(',')
        unit = str(data_c[0:1]).replace("['[\\'", '').replace("\"']", "")
        if nom == "[]":
            continue
        else:
            print(nom , name, group, unit)
 
    file.close()
    return nom , name, group, sub_group, unit  

def extract_zip(price_dir):
    now = time.strftime("%d%m%y", time.localtime())
    with ZipFile(fr"{price_dir}\BjRpo_{now}_txt.zip", 'r') as zip:
        for name in zip.namelist():
            unicode_name = name.encode('cp437').decode('cp866')
            with zip.open(name) as f:
                content = f.read()
                fullpath =  os.path.join(os.getcwd() ,unicode_name)
                with open(fullpath,'wb') as f:
                    f.write(content)
         
    

if __name__ == "__main__":
    start_time = time.time()
    price_dir = fr"\\192.168.0.128\Price\Price_BjRpo"
    token = "74a3dd44-b0dd-4f66-8a6e-48b73fee2d8e"
    offset = 0
    count = 0 
    codes = {}
    extract_zip(price_dir)
    get_api_bc(offset, count, codes)
    get_from_exel(codes, token)
    get_from_price()
    stop_time = time.time()
    res = (stop_time - start_time)
    print(res)
    

    