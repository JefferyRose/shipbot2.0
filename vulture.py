import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import csv
from tqdm import tqdm

# Number of pages to scrape
NUM_PAGES = 800
# URL to scrape
BASE_URL = "https://star-hangar.com/star-citizen.html?product_list_limit=36&p="
# Maximum number of retries for failed requests
MAX_RETRIES = 5
# Timeout duration for requests
TIMEOUT = 10
# Base number of workers
BASE_WORKERS = 10
# Speed multiplier to adjust the delay between requests and number of workers
SPEED_MULTIPLIER = .1  # Adjust this value to control speed (e.g., 0.5 for faster, 2.0 for slower)
# Adjusted number of workers based on speed multiplier
NUM_WORKERS = int(BASE_WORKERS / SPEED_MULTIPLIER)

# Running counts
item_count = 0
page_unsuccessful_count = 0

# Function to scrape a single page
def scrape_page(page_num):
    global page_unsuccessful_count
    url = BASE_URL + str(page_num)
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()  # Raise HTTPError for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            product_cards = soup.find_all('div', class_='product details product-item-details')

            products = []
            for card in product_cards:
                try:
                    name_elem = card.find('a', class_='product-item-link')
                    name = name_elem.text.strip()
                    link = "https://star-hangar.com" + name_elem['href']
                    price_elem = card.find('span', class_='price')
                    price = price_elem.text.strip()
                    products.append([name, price, link])
                except AttributeError as e:
                    continue  # Skip this card if any attribute is missing

            return products
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            time.sleep(2 * SPEED_MULTIPLIER)  # Wait before retrying
    page_unsuccessful_count += 1
    return None

# Function to save results to CSV
def save_to_csv(data, filename):
    global item_count
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Price", "Link"])
        for products in data:
            if products is not None:
                for product in products:
                    writer.writerow(product)
                    item_count += 1
    print(f"Data successfully written to {filename}. Total items: {item_count}")

# Main function to scrape multiple pages concurrently
def main():
    global item_count
    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future_to_page = {executor.submit(scrape_page, page): page for page in range(1, NUM_PAGES + 1)}
        with tqdm(total=NUM_PAGES, desc="Scraping pages") as pbar:
            for future in concurrent.futures.as_completed(future_to_page):
                page_num = future_to_page[future]
                products = future.result()
                if products is not None:
                    results.append(products)
                    item_count += len(products)
                pbar.set_postfix({'Items Scraped': item_count, 'Unsuccessful Pages': page_unsuccessful_count})
                pbar.update(1)
                time.sleep(2 * SPEED_MULTIPLIER)  # Add delay to slow down the scraping

    save_to_csv(results, 'star_hangar_data.csv')
    print(f"Scraping completed in {time.time() - start_time} seconds. Total unsuccessful pages: {page_unsuccessful_count}")

if __name__ == "__main__":
    main()

