# 📅 Austin Event Crawler & Calendar Sync

A desktop automation tool that crawls local Austin events and synchronizes them directly with the **Google Calendar API**. Built with Python and packaged as a standalone macOS application.

## 🚀 Features
* **Automated Crawling:** Scrapes event data from Austin-specific sources.
* **Google Calendar Integration:** Uses OAuth 2.0 to securely sync events to a user's calendar.
* **Standalone App:** Packaged using PyInstaller for easy execution on macOS.

## 🛠️ Tech Stack
* **Language:** Python 3.13
* **APIs:** Google Calendar API (v3), Reddit (PRAW)
* **Packaging:** PyInstaller

## 🔐 Security & Setup
To run this project locally, you must provide your own Google Cloud credentials:
1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Calendar API**.
3. Download your `credentials.json` and place it in the root directory.
4. On first run, the app will generate a `token.json` after OAuth.

## 📦 Installation
1. Clone the repo: `git clone https://github.com/Jspaun-00/AustinCityEvents.git`
2. Install dependencies: `pip install google-api-python-client google-auth-oauthlib praw`
3. Run the script: `python main.py`
