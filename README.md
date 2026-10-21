# 📅 Austin Event Crawler & Google Calendar Sync Engine

<p align="center">
  <img src="assets/icon.png" width="140" alt="Austin Event Crawler Icon" />
</p>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Google Calendar API](https://img.shields.io/badge/API-Google%20Calendar%20v3-4285F4?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://developers.google.com/calendar)
[![Reddit PRAW](https://img.shields.io/badge/Scraper-Reddit%20PRAW-FF4500?style=for-the-badge&logo=reddit&logoColor=white)](https://praw.readthedocs.io)
[![PyInstaller](https://img.shields.io/badge/Packaging-PyInstaller-yellow?style=for-the-badge)](https://pyinstaller.org)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)](#)

A desktop automation pipeline that harvests local events, festivals, meetups, and community gatherings across Austin, Texas and synchronizes them directly into Google Calendar. Packaged as a standalone macOS application using PyInstaller.

---

## 🏗️ Architecture & Sync Flow

```
     +--------------------------------+       +-------------------------------+
     | Austin City Event Web Scrapers |       |  Austin Reddit Communities    |
     |   (`Austin_city_scraper.py`)   |       | (PRAW: `reddit_scraper.py`)   |
     +---------------+----------------+       +---------------+---------------+
                     |                                        |
                     +-------------------+--------------------+
                                         |
                                         v
                         +-------------------------------+
                         | Aggregator & Deduplication    |
                         |         (`main.py`)           |
                         +---------------+---------------+
                                         |
                                         | OAuth 2.0 Auth Flow
                                         v
                         +-------------------------------+
                         | Google Calendar API Client    |
                         | (`google_calendar_manager.py`)|
                         +---------------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         | Synchronized Google Calendar  |
                         +-------------------------------+
```

---

## 🚀 Key Features

* **Multi-Source Event Harvesting:** Scrapes municipal Austin event feeds alongside community discussions on Reddit (r/Austin, r/austinevents) via PRAW.
* **Automated Deduplication:** Parses dates, times, venues, and descriptions to ensure duplicate events are not created.
* **Direct Google Calendar Sync:** Leverages Google Calendar API v3 with OAuth 2.0 token caching (`token.json`) for zero-touch recurring syncs.
* **Standalone macOS Bundle:** Compiled with PyInstaller with native `.icns` application branding.

---

## 🛠️ Setup & Prerequisites

### 1. Google Cloud Credentials
1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Calendar API**.
3. Download your OAuth 2.0 Client credentials JSON and place it in the root folder as `credentials.json`.
4. On first run, a browser window will open for one-time OAuth consent, creating `token.json`.

### 2. Reddit API Configuration
Ensure your `praw.ini` contains:
```ini
[DEFAULT]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
user_agent=AustinEventCrawler/1.0
```

---

## 📦 Installation & Execution

```bash
# Clone the repository
git clone git@github.com:Jspaun-00/AustinCityEvents.git
cd AustinCityEvents

# Install required packages
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 praw

# Run crawler and sync
python3 main.py
```

---

## 🔒 Privacy & Safety
- All OAuth secrets, access tokens, and credentials are protected by `.gitignore`.