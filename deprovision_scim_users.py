import csv
import requests
import os
import sys

# Environment variables for sensitive data
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ENTERPRISE = os.getenv("ENTERPRISE")

if not GITHUB_TOKEN or not ENTERPRISE:
    print("Missing environment variables: GITHUB_TOKEN and ENTERPRISE must be set.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

SCIM_BASE_URL = f"https://api.github.com/scim/v2/enterprises/{ENTERPRISE}/Users"

def fetch_scim_user_id(email):
    """Fetch the SCIM user ID for a given email address."""
    response = requests.get(SCIM_BASE_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch SCIM users: {response.status_code} - {response.text}")
        return None

    users = response.json().get("Resources", [])
    for user in users:
        if user.get("userName") == email:
            return user.get("id")
    return None

def deprovision_user(scim_user_id):
    """Deprovision the user with the specified SCIM user ID."""
    url = f"{SCIM_BASE_URL}/{scim_user_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        print(f"Successfully deprovisioned user with SCIM ID: {scim_user_id}")
    else:
        print(f"Failed to deprovision user with SCIM ID {scim_user_id}: {response.status_code} - {response.text}")

def main(csv_file):
    """Main function to process the CSV file and deprovision users."""
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.get("email")
            if not email:
                print("Missing email in CSV row.")
                continue

            print(f"Processing email: {email}")
            scim_user_id = fetch_scim_user_id(email)
            if scim_user_id:
                deprovision_user(scim_user_id)
            else:
                print(f"SCIM user ID not found for email: {email}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deprovision_users.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    main(csv_file)
