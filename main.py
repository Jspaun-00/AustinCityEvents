import tkinter as tk
from tkinter import scrolledtext
import threading

from Austin_city_scraper import scrape_austin_city_calendar
from google_calendar_manager import (
    get_calendar_service,
    format_for_google_calendar,
    check_if_event_exists,
    add_event_to_calendar
)
# --- Configuration ---
# Your primary calendar is usually 'primary'.
# You can also find a calendar's ID in its settings on the Google Calendar website.
CALENDAR_ID = 'primary'
PAGES_TO_SCRAPE = 3

def main():
    """The core logic for the event crawler."""
    log_message("Starting the Austin Event Crawler...")

    # Step 1: Scrape for events
    log_message(f"Scraping the first {PAGES_TO_SCRAPE} pages of the City of Austin calendar.")
    scraped_events = scrape_austin_city_calendar(num_pages=PAGES_TO_SCRAPE)

    if not scraped_events:
        log_message("No events found. Exiting.")
        return

    # Step 2: Connect to Google Calendar
    service = get_calendar_service()
    if not service:
        log_message("Failed to connect to Google Calendar. Exiting.")
        return

    # Step 3: Process and add each event
    for event in scraped_events:
        if not check_if_event_exists(service, CALENDAR_ID, event['title'], event['start_time']):
            log_message(f"New event found: '{event['title']}'. Adding to calendar.")
            google_event_body = format_for_google_calendar(event)
            add_event_to_calendar(service, CALENDAR_ID, google_event_body)
        else:
            log_message(f"Event '{event['title']}' already exists in the calendar. Skipping.")

    log_message("\nCrawler finished.")

# --- GUI Setup ---

def run_crawler_thread():
    """Runs the main crawler function in a separate thread to keep the GUI responsive."""
    # Disable the button while running
    run_button.config(state=tk.DISABLED, text="Running...")
    
    crawler_thread = threading.Thread(target=main)
    crawler_thread.start()
    
    # Periodically check if the thread is done
    check_thread(crawler_thread)

def check_thread(thread):
    """Checks if the thread is still running and re-enables the button when done."""
    if thread.is_alive():
        # Check again after 100ms
        root.after(100, lambda: check_thread(thread))
    else:
        # Re-enable the button
        run_button.config(state=tk.NORMAL, text="Run Crawler")

def log_message(message):
    """Inserts a message into the GUI's text box."""
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END) # Auto-scroll to the bottom

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Austin Event Crawler")
    root.geometry("700x500")

    # Create a frame for the button
    top_frame = tk.Frame(root, pady=10)
    top_frame.pack(fill=tk.X)

    run_button = tk.Button(top_frame, text="Run Crawler", command=run_crawler_thread, font=("Helvetica", 14))
    run_button.pack()

    # Create a scrolled text widget for logging
    log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Menlo", 11))
    log_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    # Redirect print statements to our log_message function
    import sys
    sys.stdout.write = lambda msg: log_message(msg.strip())

    root.mainloop()