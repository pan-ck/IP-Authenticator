import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IOC_CSV = ROOT / 'ioc.csv' # the path to ioc.csv
ABUSE_DB_TXT = ROOT / 'abuse_db.txt' # the path to abuse_db.txt
print("IOC_CSV: \n",(IOC_CSV))
print("ABUSE_DB_TXT: \n", ABUSE_DB_TXT)

valid_IPs = [] # a list to store valid IP

# function to get the ioc list from the csv file
def get_ioc_dict() -> list:
    try: #try to open the file
        with open(IOC_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # a list including ioc dictionaries
            return_list = list(reader)
            return return_list 
    except Exception as e:
        print(f"Error when opening the file: {e}")

# function to get the abuse db list from the txt file
def get_abuse_db_list() -> list:
    try: #try to open the file
        with open(ABUSE_DB_TXT, 'r', encoding='utf-8') as file:
            return_list = []
            # append every line to the list
            for line in file:
                return_list.append(line.strip())
            return return_list
    except Exception as e:
        print(f"Error when opening the file: {e}")

# a list including ioc dictionaries
ioc_list = get_ioc_dict()
# a list including abuse db ips
abuse_db_list = get_abuse_db_list()
print(f"abuse db list: \n{abuse_db_list}")
print(f"ioc list: \n{ioc_list}")