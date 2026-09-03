import csv
valid_IPs = [] # a list to store valid IP

# function to get the ioc list from the csv file
def get_ioc_dict() -> list:
    try: #try to open the file
        with open('ioc.csv', 'r') as file:
            reader = csv.DictReader(file)
            # a list including ioc dictionaries
            return_list = list(reader)
            return return_list 
    except Exception as e:
        print(f"Error when opening the file: {e}")

# a list including ioc dictionaries
ioc_list = get_ioc_dict()
print(ioc_list[0]['ip'])