import csv
import requests
import os

ENTERPRISE = "tech-stack"  # Replace with your enterprise slug if different
API_URL_TEMPLATE = "https://api.github.com/scim/v2/enterprises/{enterprise}/Users/{scim_user_id}"
TOKEN = os.environ.get("GITHUB_TOKEN")  # Read token from environment variable

if not TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

def deprovision_user(scim_user_id):
    url = API_URL_TEMPLATE.format(enterprise=ENTERPRISE, scim_user_id=scim_user_id)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.delete(url, headers=headers)
    print(f"Deprovisioning SCIM User ID {scim_user_id}: {response.status_code}")
    if response.status_code != 204:
        print("Error:", response.text)

def main():
    with open('deprovision_users.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            deprovision_user(row['scim_user_id'])

if __name__ == "__main__":
    main()
