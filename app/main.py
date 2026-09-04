import csv
from pathlib import Path
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime

# setting paths
ROOT = Path(__file__).resolve().parent.parent
IOC_CSV = ROOT / 'ioc.csv' # the path to ioc.csv
ABUSE_DB_TXT = ROOT / 'abuse_db.txt' # the path to abuse_db.txt
LOG_DIR = ROOT / 'logs' # the path to the log directory

# loading the .env file
load_dotenv(ROOT / ".env")

# loading the API key from the .env file
AbuseIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
# checking if the API key is loaded
if not AbuseIPDB_API_KEY:
    raise ValueError("ABUSEIPDB_API_KEY is missing; save the project .env file")
print("AbuseIPDB_API_KEY loaded")

# API endpoint
ABUSEIPDB_API_ENDPOINT = "https://api.abuseipdb.com/api/v2/check"

# a function to extract the data we need
def extract_API_data(response: dict) -> dict:
    data = response['data']
    return {
        'ipAddress': data['ipAddress'],
        'abuseConfidenceScore': data['abuseConfidenceScore'],
        'countryCode': data['countryCode'],
    }

# a function to sort the API data result by score then countryCode
def sort_API_data(data_list: list) -> list:
    sorted_data = sorted(
        data_list,
        key = lambda data:(
            int(data['abuseConfidenceScore']),
            data['countryCode'].lower(),
        )
    )
    return sorted_data

# function to check the list of ips against the AbuseIPDB API
def check_ips_abuseipdb(ips: list, api_key: str) -> list:
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    results = [] # a list to store the results we want
    # check IP one by one
    try:
        for ip in ips:
            query_string = {
                'ipAddress': ip,
            }
            response = requests.get(ABUSEIPDB_API_ENDPOINT, headers=headers, params=query_string)
            response = response.json() # convert json to dict
            results.append(extract_API_data(response))
    except Exception as e:
        print(f"Error when checking the ips with AbuseIPDB API: {e}")
    results = sort_API_data(results)
    return results

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
def get_test_ip_list() -> list:
    try: #try to open the file
        with open(ABUSE_DB_TXT, 'r', encoding='utf-8') as file:
            return_list = []
            # append every line to the list
            for line in file:
                return_list.append(line.strip())
            return return_list
    except Exception as e:
        print(f"Error when opening the file: {e}")

# a function to log the sorted data into a log file
def save_log(results: list) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_file = LOG_DIR / f"log_{timestamp}.json"
    try:
        with open(log_file, 'w', encoding='utf-8') as file:
            file.write(json.dumps(results, indent=4))
    except Exception as e:
        print(f"Error when saving the log: {e}")
    print(f"Log saved to: {log_file}")

def main():
    # a list including ioc dictionaries
    ioc_list = get_ioc_dict()
    # a list including abuse db ips
    test_ip_list = get_test_ip_list()

    # print the test ip list and ioc list
    print(f"test ip list: \n{json.dumps(test_ip_list, indent=4)}")
    print(f"ioc list: \n{json.dumps(ioc_list, indent=4)}")

    # check the IPs using AbuseIPDB API
    abuseipdb_results = check_ips_abuseipdb(test_ip_list, AbuseIPDB_API_KEY)
    # print the abuseipdb results
    print(f"abuseipdb results (sorted): \n{json.dumps(abuseipdb_results, indent=4)}")

    # save the log
    save_log(abuseipdb_results)

if __name__ == "__main__":
    main()