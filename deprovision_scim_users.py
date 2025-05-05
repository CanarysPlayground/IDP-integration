import csv
import requests
import os
import sys

# GitHub API URL and headers
BASE_URL = "https://api.github.com/scim/v2/enterprises"
TOKEN = os.getenv("GITHUB_TOKEN")  # Token is passed as an environment variable
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/scim+json"
}

def get_scim_user_id(enterprise, email):
    """Fetch the SCIM User ID for a given email."""
    url = f"{BASE_URL}/{enterprise}/Users"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Failed to fetch SCIM Users: {response.status_code} {response.text}")
        sys.exit(1)
    
    users = response.json().get("Resources", [])
    for user in users:
        if user.get("emails", [{}])[0].get("value") == email:
            return user.get("id")
    
    print(f"No SCIM User ID found for email: {email}")
    return None

def delete_user(enterprise, scim_user_id):
    """Delete a user by SCIM User ID."""
    url = f"{BASE_URL}/{enterprise}/Users/{scim_user_id}"
    response = requests.delete(url, headers=HEADERS)

    if response.status_code == 204:
        print(f"Successfully deleted user with SCIM ID: {scim_user_id}")
    else:
        print(f"Failed to delete user: {response.status_code} {response.text}")

def main():
    """Main function to read CSV and delete users."""
    enterprise = os.getenv("ENTERPRISE_SLUG")  # Enterprise slug from environment variables
    csv_file = os.getenv("CSV_FILE", "users.csv")  # CSV file path

    if not TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)
    if not enterprise:
        print("Error: ENTERPRISE_SLUG environment variable is not set.")
        sys.exit(1)

    # Read the CSV file
    try:
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                email = row.get("email")
                if not email:
                    print("Email missing in row, skipping...")
                    continue

                print(f"Processing email: {email}")
                scim_user_id = get_scim_user_id(enterprise, email)
                if scim_user_id:
                    delete_user(enterprise, scim_user_id)

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
