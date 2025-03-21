from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # Correct import

def scrape_website(url):
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Apply stealth mode correctly
        stealth_sync(page)  # Use the correct function
        
        # Navigate to the target URL
        page.goto(url, timeout=60000)  # Waits up to 60 seconds to load
        
        # Extract content (modify selector based on website structure)
        content = page.locator("#wrapper > div.ec-fx-calendar-body > div > div.ec-fx-calendar-table").inner_html().strip()
        
        # Close the browser
        browser.close()
        
        return content

# Example usage
url = "https://www.cashbackforex.com/widgets/economic-calendar?ContainerId=economic-calendar-730150&DefaultTime=7_days&IsShowEmbedButton=false&DefaultTheme=plain"  # Change this to your target website
scraped_data = scrape_website(url)
print(scraped_data)