from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync  # Correct import
from bs4 import BeautifulSoup
import json
import datetime

def scrape_website(url):
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Apply stealth mode correctly
        stealth_sync(page)  # Use the correct function
        
        # Navigate to the target URL
        page.goto(url, timeout=60000)  # Waits up to 60 seconds to load
        
        # Wait for the specific element to load (modify selector based on website structure)
        page.wait_for_selector("#wrapper > div.ec-fx-calendar-body > div > div.ec-fx-calendar-table", timeout=60000)  # Waits up to 60 seconds
        print("Element loaded successfully")
        # Optionally, you can add a delay to ensure the page is fully loaded    
        page.wait_for_timeout(5000)  # Wait for 5 seconds
        print("Page loaded successfully")
        print("Taking screenshot...")
        # Take a screenshot (optional)  
        page.screenshot(path="screenshot.png")
        
        print("Screenshot taken")
        # Extract content (modify selector based on website structure)
        content = page.locator("#wrapper > div.ec-fx-calendar-body > div > div.ec-fx-calendar-table").inner_html()
        
        # Close the browser
        browser.close()
        
        return content
def parser(content, filename="data.json"):
    soup = BeautifulSoup(content, "html.parser")
    events = []
    seen_events = set()  # Track unique events
    
    # Select all event rows (based on the class attribute in the row)
    rows = soup.select("tr.ec-fx-table-event-row")
    
    for row in rows:
        # Skip rows that don't have proper structure
        if not row.get("time") or not row.select_one("div.timeString"):
            continue
            
        # Derive the date from the 'time' attribute (Unix timestamp in seconds)
        timestamp = row.get("time")
        try:
            ts = int(timestamp) if timestamp else 0
            date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        except Exception:
            date_str = None
        
        tds = row.find_all("td")
        if len(tds) < 3:
            continue

        # First column: extract time and actual value
        td1 = tds[0]
        time_div = td1.find("div", class_="timeString")
        event_time = time_div.get_text(strip=True) if time_div else None
        
        # actual is in a div with class "actual_div"
        actual_div = td1.find("div", class_="actual_div")
        actual_text = actual_div.get_text(strip=True) if actual_div else ""
        actual_value = actual_text if actual_text != "" else None

        # Second column: extract country and forecast value
        td2 = tds[1]
        country_span = td2.find("span")
        country = country_span.get_text(strip=True) if country_span else None
        consensus_div = td2.find("div", class_="consensus_div")
        forecast_text = consensus_div.get_text(strip=True) if consensus_div else ""
        forecast_value = forecast_text if forecast_text != "" else None

        # Third column: extract event name, impact and previous value
        td3 = tds[2]
        # Impact: look for a div with a class that starts with "ec-fx-impact-"
        impact_div = td3.find("div", class_=lambda x: x and "ec-fx-impact" in x)
        impact = None
        if impact_div:
            for cls in impact_div.get("class"):
                if cls.startswith("ec-fx-impact-"):
                    impact = cls.split("ec-fx-impact-")[-1]
                    break
                    
        # Event name: find the text that's directly in the flex div
        flex_div = td3.find("div", style=lambda s: s and "flex: 1" in s)
        if flex_div:
            # Get text content but exclude text from child elements
            event_name = " ".join(t.strip() for t in flex_div.stripped_strings if t.strip())
        else:
            event_name = td3.get_text(strip=True)
            
        # Previous value from the div with class "previous_div"
        previous_div = td3.find("div", class_="previous_div")
        previous_text = previous_div.get_text(strip=True) if previous_div else ""
        previous_value = previous_text if previous_text != "" else None

        # Only add events with actual meaningful data
        if event_time and country and event_name and event_name != "6D":
            # Create a unique identifier for this event
            event_key = f"{date_str}_{event_time}_{country}_{event_name}"
            
            # Skip if we've already seen this event
            if event_key in seen_events:
                continue
                
            # Add to our set of seen events
            seen_events.add(event_key)
            
            event_obj = {
                "date": date_str,
                "time": event_time,
                "country": country,
                "event": event_name,
                "impact": impact,
                "actual": actual_value,
                "forecast": forecast_value,
                "previous": previous_value
            }
            events.append(event_obj)
    
    # Save to JSON once after processing all events
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
        
    return json.dumps(events, indent=4)
# Example usage
url = "https://www.cashbackforex.com/widgets/economic-calendar?ContainerId=economic-calendar-730150&DefaultTime=7_days&IsShowEmbedButton=false&DefaultTheme=plain"  # Change this to your target website
scraped_data = scrape_website(url)
soup = BeautifulSoup(scraped_data, 'html.parser')
parsed_data = parser(scraped_data)
# Print the parsed data
print(parsed_data)  # Print the parsed JSON data
# print(soup.prettify())  # Print the prettified HTML for better readability
# print(scraped_data)