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
                "previous": previous_value,
                "source": "CashbackForex"  # Add source field
            }
            events.append(event_obj)
    
    # Load existing data if the file exists
    existing_events = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Filter out existing events that are also in the new events (based on event key)
    existing_keys = {f"{e.get('date')}_{e.get('time')}_{e.get('country')}_{e.get('event')}" for e in existing_events if e.get("source") == "CashbackForex"}
    filtered_existing = [e for e in existing_events if f"{e.get('date')}_{e.get('time')}_{e.get('country')}_{e.get('event')}" not in existing_keys or e.get("source") != "CashbackForex"]
    
    # Combine both datasets and save
    combined_events = filtered_existing + events
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_events, f, ensure_ascii=False, indent=4)
    
    return json.dumps(events, indent=4)

def forex_factory_scraper(url="https://www.forexfactory.com/calendar", filename="data.json"):
    with sync_playwright() as p:
        # Launch browser with more options
        browser = p.chromium.launch(
            headless=False,  # Try with headless=False to see what's happening
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create a context with specific options to avoid detection
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        # Apply stealth mode
        stealth_sync(page)
        
        # Navigate to the target URL
        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)  # Waits up to 60 seconds to load
        
        # Take screenshot right after navigation to see what's on the page
        page.screenshot(path="forex_factory_initial.png")
        print("Initial screenshot taken")
        
        # Wait a bit to let any scripts execute
        page.wait_for_timeout(5000)
        
        # Try to find any table on the page first
        print("Looking for any table on the page...")
        page.wait_for_selector("table", timeout=60000)
        
        # Take another screenshot to see if the page has changed
        page.screenshot(path="forex_factory_after_wait.png")
        print("Second screenshot taken")
        
        # Try to find the calendar content using a more general approach
        print("Extracting content...")
        # Get HTML content of the whole page for examination
        html_content = page.content()
        
        # Close the browser
        browser.close()
        
        # Save the HTML for inspection
        with open("forex_factory_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Parse the data using BeautifulSoup directly
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Look for a table that might contain calendar data
        tables = soup.find_all("table")
        print(f"Found {len(tables)} tables on the page")
        
        calendar_table = None
        for i, table in enumerate(tables):
            # Look for tables with rows that have typical economic calendar classes
            if table.select("tr.calendar__row") or "calendar" in str(table.get("class", "")):
                calendar_table = table
                print(f"Found calendar table (table #{i+1})")
                break
        
        if calendar_table:
            return forex_factory_parser(str(calendar_table), filename)
        else:
            print("Could not find a suitable calendar table")
            return json.dumps([], indent=4)

def forex_factory_parser(content, filename="data.json"):
    soup = BeautifulSoup(f"<table class='calendar__table'>{content}</table>", "html.parser")
    events = []
    seen_events = set()
    current_date = None
    
    # Select all calendar rows
    rows = soup.select("tr.calendar__row")
    
    for row in rows:
        # Extract date from the date cell (if present)
        date_cell = row.find("td", class_="calendar__date")
        if date_cell:
            date_span = date_cell.find("span", class_="date")
            if date_span:
                # Format: "Mon Mar 17"
                date_text = date_span.get_text(strip=True)
                try:
                    # Convert to proper date format
                    date_parts = date_text.split()
                    if len(date_parts) >= 3:
                        month = date_parts[1]
                        day = date_parts[2]
                        year = datetime.datetime.now().year  # Assume current year
                        date_obj = datetime.datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
                        current_date = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    pass
        
        # Extract time
        time_cell = row.find("td", class_="calendar__time")
        event_time = None
        if time_cell:
            time_span = time_cell.find("span")
            if time_span:
                time_text = time_span.get_text(strip=True)
                event_time = time_text
        
        # Extract currency
        currency_cell = row.find("td", class_="calendar__currency")
        country = None
        if currency_cell:
            country = currency_cell.get_text(strip=True)
        
        # Extract impact
        impact_cell = row.find("td", class_="calendar__impact")
        impact = None
        if impact_cell:
            impact_icon = impact_cell.find("span", class_=lambda c: c and "icon--ff-impact" in c)
            if impact_icon:
                if "icon--ff-impact-red" in impact_icon.get("class", []):
                    impact = "high"
                elif "icon--ff-impact-ora" in impact_icon.get("class", []):
                    impact = "medium"
                elif "icon--ff-impact-yel" in impact_icon.get("class", []):
                    impact = "low"
        
        # Extract event name
        event_cell = row.find("td", class_="calendar__event")
        event_name = None
        if event_cell:
            event_title = event_cell.find("span", class_="calendar__event-title")
            if event_title:
                event_name = event_title.get_text(strip=True)
        
        # Extract actual value
        actual_cell = row.find("td", class_="calendar__actual")
        actual_value = None
        if actual_cell:
            actual_span = actual_cell.find("span")
            if actual_span:
                actual_value = actual_span.get_text(strip=True)
                if actual_value == "":
                    actual_value = None
        
        # Extract forecast value
        forecast_cell = row.find("td", class_="calendar__forecast")
        forecast_value = None
        if forecast_cell:
            forecast_span = forecast_cell.find("span")
            if forecast_span:
                forecast_value = forecast_span.get_text(strip=True)
                if forecast_value == "":
                    forecast_value = None
        
        # Extract previous value
        previous_cell = row.find("td", class_="calendar__previous")
        previous_value = None
        if previous_cell:
            previous_span = previous_cell.find("span")
            if previous_span:
                previous_value = previous_span.get_text(strip=True)
                if previous_value == "":
                    previous_value = None
        
        # Only add events with meaningful data
        if current_date and event_time and country and event_name:
            # Create a unique identifier
            event_key = f"{current_date}_{event_time}_{country}_{event_name}"
            
            # Skip if we've already seen this event
            if event_key in seen_events:
                continue
                
            seen_events.add(event_key)
            
            event_obj = {
                "date": current_date,
                "time": event_time,
                "country": country,
                "event": event_name,
                "impact": impact,
                "actual": actual_value,
                "forecast": forecast_value,
                "previous": previous_value,
                "source": "ForexFactory"  # Add source for tracking
            }
            events.append(event_obj)
    
    # Load existing data if the file exists
    existing_events = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_events = json.load(f)
            # Add source field to existing events if they don't have it
            for event in existing_events:
                if "source" not in event:
                    event["source"] = "CashbackForex"  # Default source for existing events
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Combine both datasets and save
    combined_events = existing_events + events
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_events, f, ensure_ascii=False, indent=4)
    
    return json.dumps(events, indent=4)

# Example usage
url = "https://www.cashbackforex.com/widgets/economic-calendar?ContainerId=economic-calendar-730150&DefaultTime=7_days&IsShowEmbedButton=false&DefaultTheme=plain"  # Change this to your target website
# scraped_data = scrape_website(url)
# soup = BeautifulSoup(scraped_data, 'html.parser')
# parsed_data = parser(scraped_data)
# Print the parsed data
# print(parsed_data)  # Print the parsed JSON data
# print(soup.prettify())  # Print the prettified HTML for better readability
# print(scraped_data)
forex_factory_scraper()