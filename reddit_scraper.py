import praw
from datetime import datetime
from zoneinfo import ZoneInfo

def scrape_reddit_austin():
    """
    Scrapes posts from r/Austin with the 'Events / Meetups' flair.

    Uses PRAW to connect to the Reddit API and returns a list of
    dictionaries, where each dictionary represents a potential event.

    Returns:
        list: A list of event dictionaries with a consistent format.
    """
    print("Scraping r/Austin for events...")
    try:
        # PRAW will automatically look for the praw.ini file in the current directory
        reddit = praw.Reddit("bot1")
        # Ensure the connection is read-only
        reddit.read_only = True
        subreddit = reddit.subreddit("austin")
    except Exception as e:
        print(f"Error: Could not connect to Reddit. Check your praw.ini settings. {e}")
        return []

    scraped_events = []
    # Search for posts with the "Events / Meetups" flair.
    # Reddit's API limits searches to around 1000 results.
    for submission in subreddit.search('flair:"Events / Meetups"', sort="new", limit=25):
        # The post creation time is in UTC (as a timestamp), convert it to a datetime object
        post_time_utc = datetime.fromtimestamp(submission.created_utc)

        # Convert from UTC to Austin's local time (Central Time)
        austin_tz = ZoneInfo("America/Chicago")
        start_time = post_time_utc.astimezone(austin_tz)

        # For Reddit, we'll assume the event is the day it's posted and set a default duration (e.g., 3 hours)
        # This is a heuristic, as Reddit posts are unstructured.
        end_time = start_time + (datetime.now() - datetime.now().replace(hour=3, minute=0, second=0, microsecond=0))

        scraped_events.append({
            'title': f"[Reddit] {submission.title}",
            'start_time': start_time,
            'end_time': end_time,
            'location': "See Reddit post for details",
            'description': f"Post by u/{submission.author}. \n\n{submission.selftext}",
            'source': f"https://www.reddit.com{submission.permalink}"
        })

    print(f"Successfully scraped {len(scraped_events)} potential events from r/Austin.")
    return scraped_events

if __name__ == '__main__':
    # This block allows you to run the script directly to test the scraper
    events = scrape_reddit_austin()
    if events:
        print("\n--- Found Potential Events ---")
        # Print details for the first 5 events found
        for event in events[:5]:
            print(f"Title: {event['title']}")
            print(f"  Starts: {event['start_time'].strftime('%a, %b %d, %Y at %I:%M %p %Z')}")
            print(f"  Location: {event['location']}")
            print(f"  Source: {event['source']}\n")