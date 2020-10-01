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
            read_file = xlrd.open_workbook("./goods/goods.xlsx")
            sheet_num = read_file.sheet_by_index(0)
            barcode_e = int(sheet_num.row_values(i)[0])  
            tax_e = sheet_num.row_values(i)[10]
            
            if tax_e == "Без НДС":
                tax_e = "NDS_NO_TAX"
            elif tax_e == 0:
                tax_e = "NDS_0"
            elif tax_e == 10:
                tax_e = "NDS_10"
            elif tax_e == 20:
                tax_e = "NDS_20"
            
            name_e = sheet_num.row_values(i)[2]
            unit_e = sheet_num.row_values(i)[4]
            
            if unit_e == "Штучный":
                unit_e = "COUNTABLE"
            elif unit_e == "Мерный":
                unit_e = "SCALABLE"  
            elif unit_e == "Алкогольный":
                unit_e = "ALCOHOL"
            elif unit_e == "Одежда":
                unit_e = "CLOTHES"
            elif unit_e == "Обувь":
                unit_e = "SHOES"
            elif unit_e == "Услуга":
                unit_e = "SERVICE"
            elif unit_e == "Табачная продукция":
                unit_e = "TOBACCO"
              
            group_e = sheet_num.row_values(i)[9]   
            print(name_e, barcode_e, unit_e, tax_e , group_e )
  
            if str(f"['{barcode_e}']") in codes:
                id = str(codes[str(f"['{barcode_e}']")]) # ['b1615355-efb3-431b-ba7a-084a3b27dc5c']
                print(id, str(f"['{barcode_e}']"), "True")
                response = requests.get(f"https://kabinet.dreamkas.ru/api/v2/products/{id}",
                                        headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}",
                                        "isClosed": "true",}) 
                print(response.text)
                i += 1
            else:
                print( str(f"['{barcode_e}']"), "False") 
                response = requests.post("https://kabinet.dreamkas.ru/api/v2/products",
                                        headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}",
                                        "isClosed": "true",},
                                        json= {"name": name_e, "barcodes": [barcode_e], "tax": tax_e, "type": unit_e} )
                print(response.status_code)
                print(response.json())
                i += 1
        except IndexError:
            break
    #['4630015370841']
    #print(codes[str(f"[{barcode_e}]")], "true")
    
    #if str("['4601373005881']") in codes:
def get_from_price():
     
    file = open("./price/БЖ300004.txt", "r")
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
                with open(f".\price\{unicode_name}",'wb') as f:
                    f.write(content)
         
    

if __name__ == "__main__":
    start_time = time.time()
    price_dir = r"\\192.168.0.128\Price\Price_BjRpo"
    token = "74a3dd44-b0dd-4f66-8a6e-48b73fee2d8e"
    offset = 0
    count = 0 
    codes = {}
    #extract_zip(price_dir)
    get_api_bc(offset, count, codes)
    get_from_exel(codes, token)
    #get_from_price()
    stop_time = time.time()
    res = (stop_time - start_time)
    print(res)
    

    