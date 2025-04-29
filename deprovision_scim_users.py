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
    # Fetch the SCIM user list
    try:
        scim_users = fetch_scim_users()
        scim_user_map = {user['userName']: user['id'] for user in scim_users.get('Resources', [])}
        print("Fetched SCIM users successfully.")
    except Exception as e:
        print(f"Error fetching SCIM users: {e}")
        return

    # Read the CSV file to find users to deprovision
    try:
        with open('deprovision_users.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_name = row['scim_user_id']
                scim_user_id = scim_user_map.get(user_name)
                if scim_user_id:
                    print(f"Deprovisioning user: {user_name} (SCIM ID: {scim_user_id})")
                    success = deprovision_user(scim_user_id)
                    if success:
                        print(f"Successfully deprovisioned user: {user_name}")
                    else:
                        print(f"Failed to deprovision user: {user_name}")
                else:
                    print(f"User {user_name} not found in SCIM users.")
    except FileNotFoundError:
        print("The file 'deprovision_users.csv' was not found.")
    except Exception as e:
        print(f"Error reading the CSV file: {e}")

if __name__ == "__main__":
    main()
