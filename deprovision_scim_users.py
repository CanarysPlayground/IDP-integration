import csv
import requests
import os

ENTERPRISE = "tech-stack"  # Replace with your enterprise slug if different
API_URL_TEMPLATE = "https://api.github.com/scim/v2/enterprises/{enterprise}/Users/{scim_user_id}"
LIST_USERS_API_URL = f"https://api.github.com/scim/v2/enterprises/{ENTERPRISE}/Users"
TOKEN = os.environ.get("GITHUB_TOKEN")  # Read token from environment variable

if not TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

def fetch_scim_users():
    """Fetch all SCIM users from the enterprise."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(LIST_USERS_API_URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch SCIM users: {response.status_code} {response.text}")
    return response.json()

def get_scim_user_id_by_email(email):
    """Fetch SCIM User ID for a specific user email."""
    scim_users = fetch_scim_users()
    for user in scim_users.get("Resources", []):
        if user.get("userName") == email:
            return user.get("id")
    return None

def deprovision_user(scim_user_id):
    """Deprovision a specific SCIM user by ID."""
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
        return False
    return True

def main():
    # Read the CSV file to find users to deprovision
    try:
        with open('deprovision_users.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_email = row['scim_user_id']
                print(f"Fetching SCIM User ID for email: {user_email}")
                scim_user_id = get_scim_user_id_by_email(user_email)
                if scim_user_id:
                    print(f"Deprovisioning user: {user_email} (SCIM ID: {scim_user_id})")
                    success = deprovision_user(scim_user_id)
                    if success:
                        print(f"Successfully deprovisioned user: {user_email}")
                    else:
                        print(f"Failed to deprovision user: {user_email}")
                else:
                    print(f"SCIM User ID not found for email: {user_email}")
    except FileNotFoundError:
        print("The file 'deprovision_users.csv' was not found.")
    except Exception as e:
        print(f"Error reading the CSV file: {e}")

if __name__ == "__main__":
    main()
