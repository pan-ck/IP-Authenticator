1. What is this project
    A python script that checks IPs using AbuseIPDB API.
    Script at app/main.py

    Input needed:
    ioc.csv (a set of rules for some special IPs)
    abuse_db.txt (a list of IP we want to test)

    Output expected:
    a log showing the results of 

2. How does it work
    1. Load IPs from abuse_db.txt
    2. call AbuseIPDB CHECK for each IP (only keep IP, score, countryCode)
    3. store data as a list of dictionary format [{},{},...]
    4. 

3. 