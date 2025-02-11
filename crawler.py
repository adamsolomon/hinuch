import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Specify the website URL and the file types you're looking for
start_url = "https://poh.education.gov.il/"  # Replace with the website you want to crawl
file_types = ['.pdf', '.docx', '.xls', '.xlsx']

# Define folder paths to exclude
excluded_folders = ['/umbraco/']

# Set to store visited URLs
visited_urls = set()

# Output file where the results will be saved
output_file = "file_links_poh.txt"

# Function to check if a URL is valid and within the same domain
def is_valid(url, domain):
    parsed = urlparse(url)
    return bool(parsed.netloc) and domain in parsed.netloc

# Function to check if a URL contains any excluded folder paths
def is_excluded(url):
    for folder in excluded_folders:
        if folder in url:
            return True
    return False

# Function to find and return all links with specific file types on a page
def find_file_links(url, domain):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the title of the page
        page_title = soup.title.string.strip() if soup.title else url

        # Get all the anchor tags with 'href' attributes
        links = soup.find_all('a', href=True)
        file_links = []

        for link in links:
            href = link['href']
            full_url = urljoin(url, href)

            # Skip URLs that are in the excluded folder paths
            if is_excluded(full_url):
                continue

            # Check if the link ends with one of the specified file types
            if any(full_url.endswith(file_type) for file_type in file_types):
                file_links.append(full_url)

            # Also check if the link is an internal page to continue crawling
            if is_valid(full_url, domain) and full_url not in visited_urls:
                visited_urls.add(full_url)
                find_file_links(full_url, domain)  # Recursively visit internal links

        # Write results to the output file if file links are found
        if file_links:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\nPage Title: {page_title}\n")
                f.write(f"URL: {url}\n")
                f.write("File Links:\n")
                for file_link in file_links:
                    f.write(f"  - {file_link}\n")
                f.write("\n")

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")

# Main function to start crawling from the start URL
def crawl_website(start_url):
    domain = urlparse(start_url).netloc
    visited_urls.add(start_url)

    # Start the crawl and get all file links
    find_file_links(start_url, domain)

    print(f"File links saved to {output_file}")

# Run the crawler
crawl_website(start_url)
