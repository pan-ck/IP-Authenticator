1. What is this project
    A Python script that checks IPs from `abuse_db.txt` with the AbuseIPDB API
    Generates a unique log of the sorted results
    Print out valid IPs based on the ioc.csv rule first. If not found, determined by AbuseIPDB API.

2. How does it work
    1. Load IPs from abuse_db.txt
    2. Call AbuseIPDB CHECK for each IP (only keep IP, score, countryCode)
    3. Store the response as a list of dictionary format [{},{},...]
    4. Sort by score, then country code
    5. log the sorted results in log/
    6. Apply IOC rules from ioc.csv (allow/deny override the score)
    7. Print valid IPs: address, score, country name, ioc description (if in ioc.csv), rule (if in ioc.csv)


3. Setup
    .env file:
    ABUSEIPDB_API_KEY=your_key

    in bash:
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python3 app/main.py