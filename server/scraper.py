from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
from selenium_stealth import stealth
import random
import time
import json
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Add additional stealth options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=options)
    
    # Apply stealth settings
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver



def scrape_cashback_forex(url="https://www.cashbackforex.com/widgets/economic-calendar?ContainerId=economic-calendar-730150&DefaultTime=7days&IsShowEmbedButton=false&DefaultTheme=plain"):
    try:
        driver = get_driver()
        driver.get(url)
        
        # Random sleep to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        # Execute some random scrolling to appear more human-like
        driver.execute_script(f"window.scrollTo(0, {random.randint(100, 300)});")
        time.sleep(random.uniform(0.5, 1.5))
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div.ec-fx-calendar-body > div > div.ec-fx-calendar-table"))
        )
        content = driver.find_element(By.CSS_SELECTOR, "#wrapper > div.ec-fx-calendar-body > div > div.ec-fx-calendar-table").get_attribute("innerHTML")
        driver.save_screenshot("screenshot.png")

        content = parser_cashback_forex(content)
        return content
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if driver:
            driver.quit()

def parser_cashback_forex(content, filename="data.json"):
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
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
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

def forex_factory_scraper(url="https://www.forexfactory.com/calendar"):

    try:
        print(f"Navigating to {url}...")
        driver = get_driver()
        driver.get(url)
        
        # Random sleep to mimic human behavior
        time.sleep(random.uniform(3, 5))
        
        # Take screenshot right after navigation
        driver.save_screenshot("forex_factory_initial.png")
        print("Initial screenshot taken")
        
        # Wait a bit to let scripts execute
        time.sleep(5)
        
        # Try to find the calendar content
        print("Looking for calendar table...")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".calendar__table"))
            )
            
            # Take another screenshot to see if the page has changed
            driver.save_screenshot("forex_factory_after_wait.png")
            print("Second screenshot taken")
            
            # Extract the calendar table
            calendar_table = driver.find_element(By.CSS_SELECTOR, ".calendar__table")
            calendar_html = calendar_table.get_attribute("outerHTML")
            # print("Calendar table HTML extracted")
            
                
            return forex_factory_parser(calendar_html)
            
        except Exception as e:
            print(f"Error extracting calendar table: {str(e)}")
            
            # Get the page source for further analysis
            html_content = driver.page_source
            
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
                return forex_factory_parser(str(calendar_table))
            else:
                print("Could not find a suitable calendar table")
                return json.dumps([], indent=4)
                
    except Exception as e:
        print(f"Error in forex_factory_scraper: {str(e)}")
        return json.dumps([], indent=4)
        
    finally:
        if driver:
            driver.quit()

def forex_factory_parser(content, filename="data_forex.json"):
    # Don't wrap the content in a table - it's already a table
    soup = BeautifulSoup(content, "html.parser")
    events = []
    seen_events = set()
    current_date = datetime.now().strftime('%Y-%m-%d')  # Default to today
    events_by_date = {}  # Track events by date for debugging
    
    # Debug the HTML structure
    print(f"Parsing calendar content with {len(soup.select('tr'))} total rows")
    
    # Select all rows including day breakers
    rows = soup.select("tr")
    
    # First pass: extract all day breaker dates for debugging
    day_breaker_dates = {}
    for i, row in enumerate(rows):
        if "calendar__row--day-breaker" in row.get("class", []):
            date_span = row.find("span")
            if date_span:
                date_text = date_span.get_text(strip=True)
                day_breaker_dates[i] = date_text
    
    print(f"Found {len(day_breaker_dates)} day breaker rows")
    
    # Now process all rows
    for row in rows:
        # Check if this is a day breaker row first
        if "calendar__row--day-breaker" in row.get("class", []):
            # Extract date from day breaker row
            date_span = row.find("span")
            if date_span:
                try:
                    # Extract just the month and day portion
                    date_text = date_span.get_text(strip=True)
                    
                    # Clean up the date text - handle formats like "SunApr Apr 18"
                    if "Apr" in date_text and date_text.count("Apr") > 1:
                        # There's a duplicate month name, get just the last part
                        parts = date_text.split()
                        month_day = " ".join(parts[-2:]) if len(parts) >= 2 else date_text
                    else:
                        month_day = date_text.strip()
                        
                    year = datetime.now().year
                    # Create a cleaner date string
                    date_str = f"{month_day} {year}"
                    
                    # Try different formats for parsing
                    for fmt in ["%b %d %Y", "%B %d %Y"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            current_date = date_obj.strftime("%Y-%m-%d")
                            print(f"Found day breaker with date: {current_date}")
                            # Initialize counter for this date
                            if current_date not in events_by_date:
                                events_by_date[current_date] = 0
                            break
                        except ValueError:
                            pass
                    else:
                        raise ValueError(f"Could not parse date: {date_str}")
                        
                except Exception as e:
                    print(f"Error parsing day breaker date: {str(e)}")
                    # Fall back to just printing what we found for debugging
                    print(f"Raw date text: '{date_text}' from {date_span}")
            continue
        
        # Skip rows that aren't calendar events
        if "calendar__row" not in row.get("class", []):
            continue
        
        # For regular calendar rows, look for the date cell - but only use it if found
        # Otherwise, keep using the current_date from the day breaker
        date_cell = row.find("td", class_="calendar__date")
        if date_cell:
            date_span = date_cell.find("span", class_="date")
            if date_span:
                try:
                    month_day = date_span.find("span")
                    if month_day:
                        month_day = month_day.get_text(strip=True)
                        year = datetime.now().year
                        date_str = f"{month_day} {year}"
                        date_obj = datetime.strptime(date_str, "%b %d %Y")
                        current_date = date_obj.strftime("%Y-%m-%d")
                        print(f"Found date cell with date: {current_date}")
                        # Initialize counter for this date
                        if current_date not in events_by_date:
                            events_by_date[current_date] = 0
                except Exception as e:
                    print(f"Error parsing date cell: {str(e)}")
        
        # Extract event details - with debug info for each row
        try:
            # Extract time
            time_cell = row.find("td", class_="calendar__time")
            event_time = None
            if time_cell:
                # Time is directly in the cell, not in a span
                time_text = time_cell.get_text(strip=True)
                if time_text:
                    # Keep "All Day" and "Tentative" as valid times
                    event_time = time_text
                    print(f"Found time: {event_time}")
            
            # Extract currency
            currency_cell = row.find("td", class_="calendar__currency")
            country = None
            if currency_cell:
                country = currency_cell.get_text(strip=True)
            
            # Extract event name
            event_cell = row.find("td", class_="calendar__event")
            event_name = None
            if event_cell:
                event_title = event_cell.find("span", class_="calendar__event-title")
                if event_title:
                    event_name = event_title.get_text(strip=True)
            
            # Debug info for rows not meeting criteria
            if not (current_date and country and event_name):
                print(f"Skipping row - missing data: date={current_date}, country={country}, event_name={event_name}")
                continue

            # Extract impact and other details
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
                "source": "ForexFactory"
            }
            events.append(event_obj)
            events_by_date[current_date] = events_by_date.get(current_date, 0) + 1
            print(f"Added event: {country} - {event_name}")
        except Exception as e:
            print(f"Error processing event row: {str(e)}")
    
    # Print summary of events by date
    print("\nEvents extracted by date:")
    for date, count in sorted(events_by_date.items()):
        print(f"- {date}: {count} events")
    
    print(f"Total extracted: {len(events)} events from ForexFactory")
    
    # Load existing data if the file exists
    existing_events = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_events = json.load(f)
            # Add source field to existing events if they don't have it
            for event in existing_events:
                if "source" not in event:
                    event["source"] = "CashbackForex"
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Combine both datasets and save
    combined_events = existing_events + events
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_events, f, ensure_ascii=False, indent=4)
    
    return json.dumps(events, indent=4)

