# Google Calendar API Setup

This guide walks you through setting up Google Cloud credentials to use the Calendar Agent.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com)

## Step 1: Create a New Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown in the top navigation bar
3. Click **New Project**
4. Enter project name: `Calendar Agent`
5. Click **Create**
6. Wait for the project to be created, then select it from the project dropdown

## Step 2: Enable the Google Calendar API

1. In the left sidebar, go to **APIs & Services** > **Library**
2. Search for `Google Calendar API`
3. Click on **Google Calendar API** in the results
4. Click **Enable**

## Step 3: Create Credentials

1. After enabling the API, click **Create Credentials**
2. Select **Google Calendar API** as the API you're using
3. Select **User data** for the type of data you'll be accessing
4. Click **Next**

### Configure OAuth Consent Screen

1. Enter an **App name** (e.g., `Calendar Agent`)
2. Select your **User support email**
3. Enter your email in **Developer contact information**
4. Click **Save and Continue**

### Configure Scopes

1. Click **Add or Remove Scopes**
2. Search for and select:
   - `https://www.googleapis.com/auth/calendar.readonly` (read access)
   - `https://www.googleapis.com/auth/calendar` (full access, if needed)
3. Click **Update**
4. Click **Save and Continue**

### Create OAuth Client ID

1. Select **Desktop app** as the application type
2. Enter a name (e.g., `Calendar Agent Desktop`)
3. Click **Create**

## Step 4: Download Credentials

1. Click **Download** to save the `client_secret_*.json` file
2. Rename it to `client_secrets.json`
3. Move it to your project directory or a secure location

## Step 5: Configure Environment

Set the path to your credentials file:

```bash
export GOOGLE_CLIENT_SECRETS=/path/to/client_secrets.json
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.) to persist it.

## First Run Authentication

On first run, the application will:

1. Open a browser window for Google authentication
2. Ask you to authorize the requested scopes
3. Save a token locally for future use

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Access blocked: This app's request is invalid" | Ensure OAuth consent screen is configured |
| "The OAuth client was not found" | Check that credentials file path is correct |
| "Scope has not been granted" | Re-authenticate and approve all requested scopes |
| Token expired | Delete the saved token file and re-authenticate |

## Security Notes

- Never commit `client_secrets.json` to version control
- Add it to your `.gitignore`:
  ```
  client_secrets.json
  *_token.json
  ```
- For production use, consider using a service account instead
