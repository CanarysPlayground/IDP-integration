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
GITHUB_USERS_API_URL = "https://api.github.com/search/users"

CSV_FILE = "users_to_deprovision.csv"  # Hardcoded CSV file name


def fetch_github_username(email):
    """Fetch the GitHub username associated with the given email address."""
    params = {"q": f"{email} in:email"}
    response = requests.get(GITHUB_USERS_API_URL, headers=HEADERS, params=params)

    # Debugging: Print GitHub API response details
    print(f"GitHub Users API URL: {GITHUB_USERS_API_URL}")
    print(f"Request Parameters: {params}")
    print(f"GitHub API Response Status: {response.status_code}")
    print(f"GitHub API Response Body: {response.text}")

    if response.status_code != 200:
        print(f"Failed to fetch GitHub username for email {email}: {response.status_code} - {response.text}")
        return None

    users = response.json().get("items", [])
    if not users:
        print(f"No GitHub user found for email: {email}")
        return None

    username = users[0].get("login")
    print(f"Found GitHub username for email {email}: {username}")
    return username


def fetch_scim_user_id(username):
    """Fetch the SCIM user ID for a given GitHub username, handling pagination."""
    start_index = 1
    count = 100  # Number of users to fetch per page

    while True:
        params = {"startIndex": start_index, "count": count}
        response = requests.get(SCIM_BASE_URL, headers=HEADERS, params=params)

        # Debugging: Print SCIM API response details
        print(f"SCIM API URL: {SCIM_BASE_URL}")
        print(f"Request Parameters: {params}")
        print(f"SCIM API Response Status: {response.status_code}")
        print(f"SCIM API Response Body: {response.text}")

        if response.status_code != 200:
            print(f"Failed to fetch SCIM users: {response.status_code} - {response.text}")
            return None

        users = response.json().get("Resources", [])
        print(f"Fetched {len(users)} users from SCIM API.")

        for user in users:
            # Match username with SCIM userName field
            if user.get("userName") == username:
                print(f"Found SCIM user ID for username {username}: {user.get('id')}")
                return user.get("id")

        # Check if there are more pages
        total_results = response.json().get("totalResults", 0)
        print(f"Total SCIM results: {total_results}, Current startIndex: {start_index}")
        if start_index + count > total_results:
            break

        start_index += count

    print(f"SCIM user ID not found for username: {username}")
    return None


def deprovision_user(scim_user_id):
    """Deprovision the user with the specified SCIM user ID."""
    url = f"{SCIM_BASE_URL}/{scim_user_id}"
    response = requests.delete(url, headers=HEADERS)

    # Debugging: Print details about the deprovisioning request
    print(f"Deprovision URL: {url}")
    print(f"Deprovision Response Status: {response.status_code}")
    print(f"Deprovision Response Body: {response.text}")

    if response.status_code == 204:
        print(f"Successfully deprovisioned user with SCIM ID: {scim_user_id}")
    else:
        print(f"Failed to deprovision user with SCIM ID {scim_user_id}: {response.status_code} - {response.text}")


def main():
    """Main function to process the CSV file and deprovision users."""
    if not os.path.exists(CSV_FILE):
        print(f"CSV file '{CSV_FILE}' not found.")
        sys.exit(1)

    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.get("email")
            if not email:
                print("Missing email in CSV row.")
                continue

            print(f"Processing email: {email}")
            github_username = fetch_github_username(email)
            if not github_username:
                continue

            scim_user_id = fetch_scim_user_id(github_username)
            if scim_user_id:
                deprovision_user(scim_user_id)
            else:
                print(f"SCIM user ID not found for username: {github_username}")


if __name__ == "__main__":
    main()
