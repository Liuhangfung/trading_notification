from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Target URL
URL = "https://farside.co.uk/bitcoin-etf-flow-all-data"

def fetch_data_with_playwright():
    # Start Playwright
    with sync_playwright() as p:
        # Launch a headless Chromium browser
        browser = p.chromium.launch(headless=False)  # Set headless=False for debugging
        page = browser.new_page()

        try:
            # Open the target URL
            page.goto(URL, wait_until="domcontentloaded", timeout=120000)

            # Wait for the table to load (broader selector)
            page.wait_for_selector("table", timeout=120000)

            # Get the page content
            content = page.content()
            print(content)  # Debug: Print the full HTML to locate the table

        except Exception as e:
            print(f"Error fetching the page: {e}")
            browser.close()
            return {}

        # Close the browser
        browser.close()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Locate the table
        table = soup.find('table')  # Broader selector
        if not table:
            print("No table found.")
            return {}

        # Locate the tbody within the table
        tbody = table.find('tbody')
        if not tbody:
            print("No <tbody> tag found in the table.")
            return {}

        # Extract rows from the tbody
        rows = tbody.find_all('tr')
        if not rows:
            print("No rows found in the table body.")
            return {}

        # Extract data from the top 5 rows
        top_5_data = []
        for row in rows[:5]:  # Process only the top 5 rows
            cols = row.find_all('td')
            if len(cols) >= 4:  # Ensure there are at least 4 columns
                date = cols[0].text.strip()  # Extract the date
                ibit = float(cols[1].text.strip().replace(",", ""))  # Extract IBIT value
                fbtc = float(cols[2].text.strip().replace(",", ""))  # Extract FBTC value
                bitb = float(cols[3].text.strip().replace(",", ""))  # Extract BITB value
                top_5_data.append({"Date": date, "IBIT": ibit, "FBTC": fbtc, "BITB": bitb})

        return top_5_data

def display_data(data):
    if not data:
        print("No data available.")
        return

    print("📊 Extracted Data (Top 5 Rows):\n")
    print(f"{'Date':<15}{'IBIT':<10}{'FBTC':<10}{'BITB':<10}")
    print("-" * 40)
    for entry in data:
        print(f"{entry['Date']:<15}{entry['IBIT']:<10.2f}{entry['FBTC']:<10.2f}{entry['BITB']:<10.2f}")

if __name__ == "__main__":
    print("Fetching data from the webpage...")
    data = fetch_data_with_playwright()
    display_data(data)
