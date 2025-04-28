# GitHub EMU Configuration with Google Identity Provider

---

## 1. Overview

This document describes how to:

- Integrate **GitHub Enterprise Managed Users (EMU)** with **Google Identity Provider** .
- Perform **user provisioning** and **deprovisioning** using GitHub's **SCIM REST APIs**.
- Automate **provisioning** and **deprovisioning** using **GitHub Actions**.

Reference:

- [GitHub SCIM Provisioning Documentation](https://docs.github.com/en/enterprise-cloud@latest/admin/managing-iam/provisioning-user-accounts-with-scim/configuring-scim-provisioning-for-users#configuring-provisioning-for-other-identity-management-systems)
- [GitHub SCIM REST API](https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/scim?apiVersion=2022-11-28)

---

## 2. Prerequisites

- GitHub Enterprise account with EMU enabled.
- Admin access to Google Identity Platform (or your SCIM-compliant IdP).
- SCIM Provisioning URL and OAuth Bearer Token from GitHub.

---

## 3. Steps for Configuring SCIM Provisioning

### 3.1. Generate SCIM Endpoint and Token

1. Navigate to **GitHub Enterprise Settings** → **Authentication Security**.
2. In the **Provisioning** section, select **Configure SCIM**.
3. Copy the **SCIM Endpoint URL** and **OAuth Bearer Token**.

---

### 3.2. Configure Google Identity Provider:

> Follow these steps for Google IdP:

1. Open **Google Admin Console**.
2. Go to **Apps** → **Web and Mobile Apps** → **Add App** → **Add Custom SAML App**.
3. Enter **App Name**: GitHub EMU.
4. Set up the SAML App (though SCIM is configured separately):
   - **Entity ID**: GitHub EMU URL.
   - **ACS URL**: GitHub login URL.
5. For **Provisioning (SCIM)**:
   - Enable **Automatic User Provisioning**.
   - Set the **SCIM API Endpoint** to the GitHub SCIM Endpoint.
   - Set **Authorization Method** to **Bearer Token**.
   - Paste the GitHub SCIM OAuth Token.
6. Map **user attributes** correctly:
   - `userName` → email
   - `displayName` → Full name
   - `active` → True

(Refer to your IdP's SCIM configuration guide for any custom mappings.)

---

## 4. Manual Provisioning and Deprovisioning Using GitHub REST API

If needed, you can **provision** or **deprovision** users manually using GitHub's SCIM API.

### 4.1. Provision a User (Create User)

**Endpoint:**

```
POST https://api.github.com/scim/v2/enterprises/{enterprise}/Users
```

**Request Headers:**

```http
Authorization: Bearer <your_token>
Accept: application/scim+json
Content-Type: application/scim+json
```

**Sample Request Body:**

```json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User"
  ],
  "userName": "user@example.com",
  "name": {
    "givenName": "First",
    "familyName": "Last"
  },
  "emails": [
    {
      "primary": true,
      "value": "user@example.com",
      "type": "work"
    }
  ]
}
```

### 4.2. Deprovision a User (Delete User)

**Endpoint:**

```
DELETE https://api.github.com/scim/v2/enterprises/{enterprise}/Users/{scim_user_id}
```

**Request Headers:**

```http
Authorization: Bearer <your_token>
Accept: application/scim+json
```

**Notes:**

- `{scim_user_id}` is the SCIM ID, not GitHub login.
- You can retrieve the `scim_user_id` using the [List SCIM Users API](https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/scim?apiVersion=2022-11-28#list-provisioned-identities).

### 4.3. Helpful Tip: Fetch SCIM User ID

**Endpoint:**

```
GET https://api.github.com/scim/v2/enterprises/{enterprise}/Users
```

This will list all provisioned users along with their SCIM IDs.

---

## 5. Automating Provisioning and Deprovisioning with GitHub Actions

You can automate the process of **provisioning** and **deprovisioning** users via **GitHub Actions**.

### 5.1. Overview

- Whenever a user is added or removed in the **Google IdP App**, a GitHub Action can trigger.
- The Action will call the same **REST APIs** to provision or deprovision the users automatically in GitHub EMU.

### 5.2. Example GitHub Action for Provisioning

```yaml
name: Provision GitHub EMU User

on:
  workflow_dispatch:

jobs:
  provision-user:
    runs-on: ubuntu-latest
    steps:
      - name: Provision User
        run: |
          curl -X POST https://api.github.com/scim/v2/enterprises/${{ secrets.GITHUB_ENTERPRISE }}/Users \
          -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
          -H "Accept: application/scim+json" \
          -H "Content-Type: application/scim+json" \
          -d '{
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "userName": "user@example.com",
                "name": {"givenName": "First", "familyName": "Last"},
                "emails": [{"primary": true, "value": "user@example.com", "type": "work"}]
              }'
```

### 5.3. Example GitHub Action for Deprovisioning

```yaml
name: Deprovision GitHub EMU User

on:
  workflow_dispatch:

jobs:
  deprovision-user:
    runs-on: ubuntu-latest
    steps:
      - name: Deprovision User
        run: |
          curl -X DELETE https://api.github.com/scim/v2/enterprises/${{ secrets.GITHUB_ENTERPRISE }}/Users/${{ secrets.SCIM_USER_ID }} \
          -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
          -H "Accept: application/scim+json"
```

### 5.4. Secrets Required

- `GITHUB_TOKEN`: Your GitHub OAuth token with SCIM access.
- `GITHUB_ENTERPRISE`: Your GitHub Enterprise slug.
- `SCIM_USER_ID`: SCIM ID for the user to deprovision.

---

## 6. Important Points

- **OAuth Bearer Token** needs to be refreshed as per your enterprise token policy.
- SCIM provisioning will not work unless SSO login is configured and EMU is enabled.
- Deprovisioning a user via SCIM does **NOT** delete their historical contributions; it only disables the GitHub account.
- Use GitHub Actions carefully and limit access to secrets.

---

## 7. References

- [Provision a SCIM Enterprise User API](https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/scim?apiVersion=2022-11-28#provision-a-scim-enterprise-user)
- [Delete a SCIM Enterprise User API](https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/scim?apiVersion=2022-11-28#delete-a-scim-user-from-an-enterprise)
- [Configuring SCIM Provisioning for Users](https://docs.github.com/en/enterprise-cloud@latest/admin/managing-iam/provisioning-user-accounts-with-scim/configuring-scim-provisioning-for-users)

---
## Note: 
The process outlined will remain the same for other IDPs as well.
