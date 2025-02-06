import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

import time
import sys
import threading

# Timer function that updates the terminal
def timer():
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        timer_display = f"\rElapsed Time: {minutes:02}:{seconds:02}   |   Expected Time: ~ 9:00"  # Format time as MM:SS
        sys.stderr.write(timer_display)
        sys.stderr.flush()
        time.sleep(1)

# Function to start the timer in a separate thread
def start_timer():
    timer_thread = threading.Thread(target=timer)
    timer_thread.daemon = True  # This ensures the timer thread stops when the main program exits
    timer_thread.start()

# Set to store visited URLs
visited_urls = set()

# Set to store external URLS
external_urls = set()

# Define the base URL for the directory
BASE_URL = 'https://sci.fi.ncsu.edu/cybersecurity/'

# Function to check if a URL is a valid internal URL (within the cybersecurity directory)
def is_internal_url(url):
    parsed_url = urlparse(url)
    base_parsed_url = urlparse(BASE_URL)
    return parsed_url.netloc == base_parsed_url.netloc and parsed_url.path.startswith(base_parsed_url.path)

# Function to check if a URL is an external URL
def is_external_url(url):
    parsed_url = urlparse(url)
    base_parsed_url = urlparse(BASE_URL)
    return parsed_url.netloc != base_parsed_url.netloc

def is_url_alive(url):
    try:
        # Define a user-agent to mimic a real browser (some websites block non-browser requests)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use GET request with headers and a timeout to handle potential slow responses
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=2)  # Increased timeout

        # If status code starts with 2xx, consider it alive
        return response.status_code >= 200 and response.status_code < 300
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return False

# Function to extract links from a given URL and record their positions
def extract_links(url):
    try:
        # Send a request to get the page content
        response = requests.get(url, timeout=15)  # Increased timeout
        response.raise_for_status()  # Check if request was successful
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all the <a> tags with href attributes
        links = soup.find_all('a', href=True)
        
        # Store information about each link
        link_info = []
        for idx, link in enumerate(links):
            link_url = urljoin(url, link['href'])  # Absolute URL of the link
            # If it's an internal URL, add it for recursive crawling
            if link_url not in visited_urls and not link_url.startswith("mailto") and not link_url.endswith("#main-content"):
                if is_internal_url(link_url):
                    link_info.append({
                        "external": False,
                        "link_url": link_url,
                        "line_number": idx + 1,
                        "page_url": url,
                        "status": "Alive"
                    })
                elif is_external_url(link_url):
                    link_info.append({
                        "external": True,
                        "link_url": link_url,
                        "line_number": idx + 1,
                        "page_url": url,
                        "status": "Alive" if is_url_alive(link_url) else "Broken"
                    })
        
        return link_info

    except requests.exceptions.RequestException as e:
        print(f"Request error with {url}: {e}")
        return []

# Function to recursively crawl internal URLs and collect external URLs
def scrape_website(start_url):
    # Start timer
    start_timer()

    # Start with the given URL
    to_visit = [start_url]
    all_links = []
        
    # Iterate through URLs to check them concurrently
    while to_visit:
        current_url = to_visit.pop()
        
        # If we have already visited this URL, skip it
        if current_url in visited_urls:
            continue
        
        # Mark this URL as visited
        visited_urls.add(current_url)
        print(f"\nVisiting: {current_url}")
        
        # Extract links from the current page
        links = extract_links(current_url)
        
        # Add the new internal links to the to_visit list and prepare external links for concurrent checking
        for link in links:
            all_links.append(link)
            if link['external'] == False and link['link_url'] not in visited_urls and not link['link_url'].endswith("#main-content"):
                to_visit.append(link["link_url"])                     

    return all_links

# Main function to start scraping from a given website
if __name__ == "__main__":
    links = scrape_website(BASE_URL)
    print(f"Scraping finished. Found {len(visited_urls)} links.")
