from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# The URL for the City of Austin's main event calendar
# The URL for the City of Austin's full event calendar, which is better for scraping
CITY_CALENDAR_URL = "https://www.austintexas.gov/fullcalendar?department=1807"

def scrape_austin_city_calendar(num_pages=1):
    """
    Scrapes events from the City of Austin's official event calendar.

    Args:
        num_pages (int): The number of pages to scrape. Defaults to 1.

    Fetches the HTML from the calendar pages, parses it to find event details,
    and returns a list of dictionaries, where each dictionary represents an event.

    Returns:
        list: A list of event dictionaries. Each dictionary contains:
              'title' (str): The name of the event.
              'start_time' (datetime): The start date and time of the event.
              'end_time' (datetime): The end date and time of the event.
              'location' (str): The event's location.
              'description' (str): A short description or link to the event details.
              'source' (str): The source URL of the event.
    """
    print("Scraping City of Austin calendar using Playwright...")
    try:
        page = None # Define page here to ensure it's in scope for the exception block
        scraped_events = []
        with sync_playwright() as p:
            # For debugging, you can see the browser by setting headless=False
            # browser = p.chromium.launch(headless=False, slow_mo=500)
            # Use the system's installed Chrome browser instead of bundling one.
            browser = p.chromium.launch(channel="chrome")

            page = browser.new_page()

            for page_num in range(num_pages):
                # Page 1 is at page=0, Page 2 is at page=1, and so on.
                page_url = f"{CITY_CALENDAR_URL}&page={page_num}"
                print(f"Scraping page {page_num + 1} of {num_pages}: {page_url}")
                page.goto(page_url, timeout=30000)

                # Wait for the first event item to appear to ensure the list is loaded
                page.wait_for_selector("div.views-field-title", timeout=20000)

                # Locate all event rows using Playwright's locators
                event_rows = page.locator('div.view-content div[class*="col-xs-12"]').all()

                for event_row in event_rows:
                    try:
                        # --- Extract Title and URL ---
                        title_element = event_row.locator('h3.field-content a')
                        title = title_element.inner_text()
                        event_url_path = title_element.get_attribute('href')
                        event_url = f"https://www.austintexas.gov{event_url_path}"

                        # --- Extract Date and Time ---
                        # The page uses <time> tags with a datetime attribute
                        time_tags = event_row.locator('time').all()
                        if not time_tags:
                            continue # Skip if no time tags are found

                        start_time_str = time_tags[0].get_attribute('datetime')
                        start_time_utc = datetime.fromisoformat(start_time_str)

                        # Use the last time tag for the end time, or the start time if only one exists
                        end_time_str = time_tags[-1].get_attribute('datetime')
                        end_time_utc = datetime.fromisoformat(end_time_str)

                        # Convert from UTC to Austin's local time (Central Time)
                        austin_tz = ZoneInfo("America/Chicago")
                        start_time = start_time_utc.astimezone(austin_tz)
                        original_end_time = end_time_utc.astimezone(austin_tz)

                        # --- Heuristic for Recurring Events ---
                        # If the event duration is longer than 24 hours, assume it's a recurring series.
                        # Adjust the end time to be 3 hours after the start time for a more useful calendar entry.
                        event_description = "More details available at the official event page."
                        if (original_end_time - start_time).days > 0:
                            end_time = start_time + timedelta(hours=3)
                            event_description = f"NOTE: This is a recurring event series. The calendar entry has been shortened. Please check the source link for all dates and times.\n\n{event_description}"
                        else:
                            end_time = original_end_time

                        # --- Extract Location ---
                        location_element = event_row.locator('div.views-field-field-address')
                        location = location_element.inner_text().strip() if location_element.count() > 0 else "Location not specified"
                        scraped_events.append({
                            'title': title,
                            'start_time': start_time,
                            'end_time': end_time,
                            'location': location,
                            'description': event_description,
                            'source': event_url
                        })
                    except (AttributeError, KeyError, TypeError) as e:
                        print(f"Skipping a malformed event entry. Error: {e}")
                        continue
            browser.close()
    except (PlaywrightTimeoutError, Exception) as e:
        if page:
            # Take a screenshot on failure to help with debugging
            error_screenshot_path = "error_screenshot.png"
            print(f"Error: Could not process the calendar page with Playwright. {e}")
            print(f"Saving a screenshot of the page to {error_screenshot_path} for debugging.")
            page.screenshot(path=error_screenshot_path, full_page=True)
        else:
            print(f"An error occurred before the page could be loaded: {e}")
        return []

    print(f"Successfully scraped {len(scraped_events)} events from the City of Austin calendar.")
    return scraped_events

if __name__ == '__main__':
    # This block allows you to run the script directly to test the scraper
    events = scrape_austin_city_calendar()
    if events:
        print("\n--- Found Events ---")
        # Print details for the first 5 events found
        for event in events[:5]:
            print(f"Title: {event['title']}")
            print(f"  Starts: {event['start_time'].strftime('%a, %b %d, %Y at %I:%M %p %Z')}")
            print(f"  Ends:   {event['end_time'].strftime('%a, %b %d, %Y at %I:%M %p %Z')}")
            print(f"  Location: {event['location']}")
            print(f"  Source: {event['source']}\n")
