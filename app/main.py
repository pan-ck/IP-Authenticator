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

# API endpoint
ABUSEIPDB_API_ENDPOINT = "https://api.abuseipdb.com/api/v2/check"

# a function to extract the data we need
def extract_API_data(response: dict) -> dict:
    data = response['data']
    return {
        'ipAddress': data.get('ipAddress'),
        'abuseConfidenceScore': data.get('abuseConfidenceScore'),
        'countryCode': data.get('countryCode'),
        'countryName': data.get('countryName'),
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
# return a sorted list of dict{}. including IP, score, countryCode
def check_ips_abuseipdb(ips: list, api_key: str) -> list:
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    results = [] # a list to store the results we want
    # check IP one by one
    for ip in ips:
        query_string = {
            'ipAddress': ip,
            'verbose': True,
        }
        response = requests.get(ABUSEIPDB_API_ENDPOINT, headers=headers, params=query_string)
        response.raise_for_status() # raise an exception if the request is not successful
        response = response.json() # convert json to dict
        results.append(extract_API_data(response))
    results = sort_API_data(results)
    return results

# function to get the ioc list from the csv file
def get_ioc_dict() -> list:
        with open(IOC_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # a list including ioc dictionaries
            return_list = list(reader)
            return return_list 

# function to get the abuse db list from the txt file
def get_test_ip_list() -> list:
        with open(ABUSE_DB_TXT, 'r', encoding='utf-8') as file:
            return_list = []
            # append every line to the list
            for line in file:
                return_list.append(line.strip())
            return return_list

# a function to log the sorted data into a log file
def save_log(results: list) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_file = LOG_DIR / f"log_{timestamp}.json"
    try:
        with open(log_file, 'x', encoding='utf-8') as file:
            file.write(json.dumps(results, indent=4))
    except Exception as e:
        print(f"Error when saving the log: {e}")

# a function to check if the IP is in the ioc list
# return the ioc data dictionary if yes
def is_in_ioc(ip: str, ioc_list : list) -> dict:
    for item in ioc_list:
        if item['ip'] == ip:
            return item
    return None

# input an IP and an ioc data dictionary, output true if IP is allow, else false
def check_ip_ioc_rule(ioc_data: dict) -> bool:
    return ioc_data['rule'] == 'allow'

# input abuseipdb results and ioc list, return a list of valid IPs with details
def ip_authenticator(abuseipdb_results: list, ioc_list: list) -> list:
    results_list = []
    for result in abuseipdb_results:
        ioc_data = is_in_ioc(result['ipAddress'], ioc_list)
        # handle the case where the IP is in the ioc list
        if ioc_data:
            if check_ip_ioc_rule(ioc_data):
                item = dict(result)
                item['ioc description'] = ioc_data['description']
                item['rule name'] = ioc_data['rule']
                results_list.append(item) # if the IP is valid, add the result to the results_list
            continue # if the IP is not valid, continue to the next IP
        # handle the case where the IP is not in the ioc list
        if result['abuseConfidenceScore'] <= 25:
            results_list.append(result) 
    return results_list

def main():
    # a list including ioc dictionaries
    ioc_list = get_ioc_dict()
    # a list including abuse db ips
    test_ip_list = get_test_ip_list()

    # check the IPs using AbuseIPDB API
    abuseipdb_results = check_ips_abuseipdb(test_ip_list, AbuseIPDB_API_KEY)
    
    # save the abuseipdb results to a log file
    save_log(abuseipdb_results)

    # authenticate the IPs
    authenticated_ips = ip_authenticator(abuseipdb_results, ioc_list)
    # print the authenticated ips
    print(f"valid ips: \n{json.dumps(authenticated_ips, indent=4)}")

if __name__ == "__main__":
    main()