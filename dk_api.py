""" Импортируем необходимые библиотеки"""

import os 
import requests
import json 
import xlrd
import time

from zipfile import ZipFile

""" get_devices_from_api() позволяет получить id кассы из API """

def get_devices_from_api():
    devices = []
    response = requests.get(f"https://kabinet.dreamkas.ru/api/devices",
                            headers={"Content-Type": "application/json",
                                    "Authorization": f"Bearer {token}",
                                    "isClosed": "true",}) 
    get_device = json.loads(response.text)
    with open("./devices/devices.json", "w", encoding="utf-8") as write_file: # Записываем результат get запроса в json файл с кодировкой utf-8
        json.dump(get_device, write_file, indent=4, ensure_ascii=False) # ensure_ascii=False чтобы не было проблем с кириллицей
    with open("./devices/devices.json", "r", encoding="utf-8") as read_file: # Чтение из json файла
        data = json.load(read_file)
        for iter in range(len(data)): # Итерируемся по каждой кассе
            try:
                devices.append({"deviceId": data[iter]["id"], "value": 0}) # Добавляем цены всем кассам (добавить "value": int)               
            except IndexError:
                break   
    print(devices)
    return  devices 
      
""" get_departments_from_api() позволяет получить словарь id отделов из API ( 'name': 'id')"""

def get_departments_from_api():
    offset = 0
    departments = {} 
    while True:
        try:
            response = requests.get("https://kabinet.dreamkas.ru/api/v2/departments",
                                    headers={"Content-Type": "application/json",
                                            "Authorization": f"Bearer {token}",
                                            "isClosed": "true",},
                                    params={"limit": 1000,"offset": offset},)
            get_departments = json.loads(response.text)
            with open("./departments/departments.json", "w", encoding="utf-8") as write_file:  # Записываем результат get запроса в json файл с кодировкой utf-8
                json.dump(get_departments, write_file, indent=4, ensure_ascii=False) # ensure_ascii=False чтобы не было проблем с кириллицей
            with open("./departments/departments.json", "r", encoding="utf-8") as read_file: # Чтение из json файла
                json.load(read_file)
                for iter in range(1000): # Итерируемся по каждому отделу 
                    departments[str(get_departments[iter]['name'])] =  str([get_departments[iter]['id']]).strip("[").strip("]").strip("'")
            offset += 1000
        
        except PermissionError:
            break
  
        except IndexError:
            break
    return departments



def get_api_barcodes(offset, codes):
    while True:
        try:
            response = requests.get("https://kabinet.dreamkas.ru/api/products",
                                    headers={"Content-Type": "application/json",
                                            "Authorization": f"Bearer {token}",
                                            "isClosed": "true",},
                                    params={"limit": 1000,"offset": offset},)
            get_file = json.loads(response.text)
            with open("./barcodes/barcodes.json", "a", encoding="utf-8") as write_file:
                json.dump(get_file, write_file, indent = 4, ensure_ascii=False)
                for iter in range(1000):
                    codes[str(get_file[iter]['barcodes'])] =  str([get_file[iter]['id']]).strip("[").strip("]").strip("'")
                #print(str([get_file[iter]['id']]).strip("[").strip("]").strip("'"))  
                                  
            offset += 1000
        except PermissionError:
            break
  
        except IndexError:
            break
    return codes

def get_from_exel(codes ,token, devices):
    i = 1
    while i != IndexError:
        try:
            read_file = xlrd.open_workbook("./goods/si.xlsx")
            sheet_num = read_file.sheet_by_index(0)
            barcode_e = int(sheet_num.row_values(i)[0])  
            name_e = sheet_num.row_values(i)[2]
            price = sheet_num.row_values(i)[3]
            unit_e = sheet_num.row_values(i)[4]
            quantity_e = sheet_num.row_values(i)[8]
            tax_e = sheet_num.row_values(i)[10]
            print(type(quantity_e))
            if tax_e == "Без НДС":
                tax_e = "NDS_NO_TAX"
            elif tax_e == 0:
                tax_e = "NDS_0"
            elif tax_e == 10:
                tax_e = "NDS_10"
            elif tax_e == 20:
                tax_e = "NDS_20"
            
            
            if unit_e.capitalize() == "Штучный" and "Сиг-ты"  not in name_e: #Защита от Ромашова
                print(unit_e.capitalize())
                unit_e = "COUNTABLE"
                if quantity_e == 1.0:
                    quantity_e = 1000
                    unit = "796"
                    json_add = {"name": name_e,"barcodes": [barcode_e], "tax": tax_e, "type": unit_e, "quantity": quantity_e, "unit": unit, "prices": devices,}
            
            elif unit_e.capitalize() == "Штучный" and "Сиг-ты" in name_e: #Защита от Ромашова
                unit_e = "TOBACCO"
                if quantity_e == 1.0:
                    quantity_e = 1000
                    unit = "796"
                    json_add = {"name": name_e,"barcodes": [barcode_e], "tax": tax_e, "isMarked": "true", "type": unit_e, "quantity": quantity_e, "unit": unit, "prices": devices,}


            elif unit_e.capitalize() == "Весовой": #Защита от Ромашова
                unit_e = "SCALABLE" 
                if quantity_e == 0.001:
                    quantity_e = 1
                    unit = "166"
                    json_add = {"name": name_e,"vendorCodes": [barcode_e], "tax": tax_e, "type": unit_e, "quantity": quantity_e, "unit": unit, "prices": devices,}
            elif unit_e.capitalize() == "Табак":
                unit_e = "TOBACCO"
                if quantity_e == 1.0:
                    quantity_e = 1000
                    unit = "796"
                    json_add = {"name": name_e,"barcodes": [barcode_e], "tax": tax_e, "isMarked": "true", "type": unit_e, "quantity": quantity_e, "unit": unit, "prices": devices,}
                    if "2" in str(barcode_e)[0]:
                        i+=1
                    
 
              

            elif unit_e == "Алкогольный":
                unit_e = "ALCOHOL"
            elif unit_e == "Одежда":
                unit_e = "CLOTHES"
            elif unit_e == "Обувь":
                unit_e = "SHOES"
            elif unit_e == "Услуга":
                unit_e = "SERVICE"

            
            group_e = sheet_num.row_values(i)[9]   
            #print(name_e, barcode_e, unit_e, tax_e , group_e )
                       
            """Ищем штрихкод в кабинете Дримкас"""
                       
            if str(f"['{barcode_e}']") in codes:
                id = str(codes[str(f"['{barcode_e}']")]) # ['b1615355-efb3-431b-ba7a-084a3b27dc5c']
                #print(id, str(f"['{barcode_e}']"), "True")
                response = requests.get(f"https://kabinet.dreamkas.ru/api/v2/products/{id}",
                                        headers={"Content-Type": "application/json",
                                                "Authorization": f"Bearer {token}",
                                                "isClosed": "true",}) 
                get_file = json.loads(response.text)
                print(get_file)


                if tax_e == get_file['tax']:
                    print(tax_e, get_file['tax'], "true")
                
                elif  tax_e != get_file['tax']:
                    response = requests.patch(f"https://kabinet.dreamkas.ru/api/v2/products/{id}",
                                        headers={"Content-Type": "application/json",
                                                "Authorization": f"Bearer {token}",
                                                "isClosed": "true",},
                                        json= json_add)
                    print(tax_e, get_file['tax'], "false")
            

                    
                #print(response.text)
                i += 1
            elif str(f"['{barcode_e}']") not in codes:
                #print( str(f"['{barcode_e}']"), "False") 
                response = requests.post(f"https://kabinet.dreamkas.ru/api/v2/products/",
                                        headers={"Content-Type": "application/json",
                                                "Authorization": f"Bearer {token}",
                                                "isClosed": "true",},
                                        json= json_add)

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
            continue
            #print(nom , name, group, unit)
 
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
    """74a3dd44-b0dd-4f66-8a6e-48b73fee2d8e"""
    token = "de43a3c5-4505-4c57-bdc4-3d34d503a2b1"
    offset = 0
    codes = {}                                   
    #extract_zip(price_dir)
    #get_departments_from_api()
    get_devices_from_api()
    get_api_barcodes(offset, codes)
    get_from_exel(codes, token, get_devices_from_api())
    #get_from_price()
    stop_time = time.time()
    res = (stop_time - start_time)
    print(res)
    os.remove("./barcodes/barcodes.json")
    
    

    