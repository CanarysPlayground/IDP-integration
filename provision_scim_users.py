import csv
import requests
import json
import os

API_URL = "https://api.github.com/scim/v2/enterprises/maxval/Users"
TOKEN = os.environ.get("GITHUB_TOKEN")  # Read token from environment variable

if not TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

def provision_user(row):
    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "externalId": row['externalId'],
        "active": True,
        "userName": row['userName'],
        "name": {
            "formatted": row['formatted'],
            "familyName": row['familyName'],
            "givenName": row['givenName']
        },
        "displayName": row['displayName'],
        "emails": [{
            "value": row['email'],
            "type": "work",
            "primary": True
        }],
        "roles": [{
            "value": row['role'],
            "primary": False
        }]
    }
    headers = {
        "Accept": "application/scim+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    print(f"Provisioning {row['userName']} ({row['email']}): {response.status_code}")
    if response.status_code not in (201, 200):
        print("Error:", response.text)

def main():
    with open('users.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            provision_user(row)

if __name__ == "__main__":
    main()
