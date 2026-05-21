🗓️ Chat2Cal — Simple Setup Guide

Chat2Cal turns normal text into Google Calendar events.

Example input
“Meeting with team tomorrow at 2pm”
Result
Event added to your calendar

It runs locally using LM Studio. Your data stays on your machine.

📋 Requirements

Set these up first:

Python 3.10 or higher
LM Studio installed and running
A downloaded model inside LM Studio
Examples: Llama 3, Mistral, Phi-3

🌐 Google Calendar Setup

You need a credentials.json file to connect your calendar.

Step 1. Create a project

Go to https://console.cloud.google.com/
Log in
Click “Select a project”
Click “New Project”
Name it Chat2Cal

Step 2. Enable Calendar API

Use the search bar
Search “Google Calendar API”
Click it
Click Enable

Step 3. Set up consent screen

Click “OAuth consent screen”
Choose External
Click Create

Fill in:

App name: Chat2Cal
User support email: your Gmail
Developer email: your Gmail
Click Save and Continue
Go to Test Users
Click Add Users
Add your Gmail

Step 4. Get credentials file

Go to “Credentials”
Click “Create Credentials”
Choose “OAuth client ID”
Select Desktop App
Name it Chat2Cal Client
Click Create
Download the JSON file

Final step:

Move the file to your project folder
Rename it to credentials.json

🚀 Run the App

Step 1. Install libraries

Open terminal inside your project folder:

python -m pip install openai google-auth-oauthlib google-auth-httplib2 google-api-python-client

💡 What happens next

You type a message
LM Studio processes it
The app extracts:
Title
Date
Start time
End time
Location
Description
Event gets added to Google Calendar