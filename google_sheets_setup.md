# Google Sheets Setup Guide for Colour Perception Experiment

## Overview
This guide shows how to set up Google Sheets as a free cloud database for your Streamlit app. Works perfectly with Streamlit Community Cloud free tier!

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Note your project ID

## Step 2: Enable Google Sheets API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"
4. Also enable "Google Drive API"

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Give it a name (e.g., "colour-experiment-app")
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

## Step 4: Generate Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Click "Create"
6. A JSON file will download - **keep this safe!**

The JSON file looks like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

## Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Colour Perception Experiment" (or whatever you prefer)
4. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
   ```
5. **Important:** Share the spreadsheet with the service account email
   - Click "Share" button
   - Paste the `client_email` from your JSON file
   - Give it "Editor" access
   - Uncheck "Notify people"
   - Click "Share"

## Step 6: Configure Streamlit Secrets

### For Local Testing:
Create `.streamlit/secrets.toml` in your project directory:

```toml
# Google Sheets Configuration
spreadsheet_id = "YOUR_SPREADSHEET_ID_HERE"

# Or use spreadsheet name instead:
# spreadsheet_name = "Colour Perception Experiment"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### For Streamlit Cloud Deployment:

1. Push your code to GitHub (WITHOUT the secrets.toml file!)
2. Deploy on [share.streamlit.io](https://share.streamlit.io)
3. Go to your app settings (click ⋮ menu > "Settings")
4. Click "Secrets" in the left sidebar
5. Paste the same content from above
6. Click "Save"

**Security Note:** Never commit secrets.toml or the service account JSON to GitHub!

## Step 7: Test Your Setup

Run locally:
```bash
streamlit run colour_experiment_muthu.py
```

The app should:
- Connect to Google Sheets automatically
- Create a "Results" worksheet if it doesn't exist
- Save all participant data to the sheet
- Allow downloading accumulated data from all participants

## Troubleshooting

**"Google Sheets credentials not configured"**
- Check that secrets.toml exists in `.streamlit/` folder
- Verify the format matches exactly (including line breaks in private_key)

**"Error accessing worksheet"**
- Make sure you shared the spreadsheet with the service account email
- Check that both Google Sheets API and Google Drive API are enabled

**"Permission denied"**
- Service account needs Editor access to the spreadsheet
- Re-share the spreadsheet if needed

## Benefits of Google Sheets

✅ **Free forever** (Google Sheets API has generous free quota)
✅ **Persistent storage** (data never lost, even on free Streamlit tier)
✅ **Real-time access** (view data in Google Sheets while experiment runs)
✅ **Easy backup** (download from Google Sheets anytime)
✅ **Collaborative** (multiple researchers can access the same sheet)

## Data Structure

The app creates a worksheet with these columns:
- participant_name
- gender
- age
- sleep_hours
- overall_trial
- spectrum
- percentage_complete
- hex_code
- rgb
- reaction_time_ms
- false_alarm
- timestamp

## Viewing Data

You can:
1. Open the Google Sheet directly to see real-time data
2. Use built-in Google Sheets analysis tools
3. Download from the app's Results page (includes ALL participants)
4. Export as Excel/CSV from Google Sheets

## Cost

**Completely FREE!**
- Google Sheets API: 500 requests/100 seconds (more than enough)
- Google Drive API: 1000 requests/100 seconds
- Streamlit Community Cloud: Free hosting

Perfect for research experiments with hundreds of participants!