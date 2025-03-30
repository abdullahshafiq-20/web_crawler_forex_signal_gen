import pandas as pd
import json
import datetime

# 🔹 Load Scraped CPI Data from JSON File
def load_cpi_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        df = pd.DataFrame(data)
        
        # Filter for CPI events only
        if 'event' in df.columns:
            cpi_df = df[df['event'].str.contains('CPI', case=False, na=False)]
            if cpi_df.empty:
                print(f"Warning: No CPI events found in {file_path}")
                # Show available events for debugging
                print(f"Available events: {df['event'].unique()[:10]}")
                
        return df
    except Exception as e:
        print(f"Error loading data from {file_path}: {str(e)}")
        return pd.DataFrame()

# 🔹 Truncate data to specific date range
def truncate_data(df, days_before=2, include_today=True, include_tomorrow=True):
    """
    Truncate the DataFrame to include only specified date range:
    - Previous N days (default: 2)
    - Today (optional)
    - Tomorrow (optional)
    
    Args:
        df (DataFrame): Input DataFrame with 'date' column
        days_before (int): Number of days before today to include
        include_today (bool): Whether to include today's data
        include_tomorrow (bool): Whether to include tomorrow's data
        
    Returns:
        DataFrame: Filtered DataFrame containing only the specified date range
    """
    if df.empty or 'date' not in df.columns:
        print("No valid data or date column for truncation")
        return df
        
    # Convert date column to datetime if it's not already
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print(f"Error converting dates: {str(e)}")
        return df
        
    # Get current date (today)
    today = pd.Timestamp.today().normalize()
    tomorrow = today + pd.Timedelta(days=1)
    
    # Calculate date range bounds
    start_date = today - pd.Timedelta(days=days_before)
    end_date = tomorrow if include_tomorrow else today
    
    # Create a list of dates to include
    date_range = []
    
    # Add previous days
    for i in range(days_before, 0, -1):
        date_range.append(today - pd.Timedelta(days=i))
    
    # Add today if requested
    if include_today:
        date_range.append(today)
        
    # Add tomorrow if requested
    if include_tomorrow:
        date_range.append(tomorrow)
    
    # Filter the DataFrame to include only the specified dates
    truncated_df = df[df['date'].dt.normalize().isin(date_range)]
    
    num_filtered = len(df) - len(truncated_df)
    
    # Create a more descriptive date range string with weekdays
    date_range_str = []
    for d in sorted(date_range):
        day_name = d.strftime('%A')
        if d == today:
            date_range_str.append(f"{d.strftime('%Y-%m-%d')} {day_name} (Today)")
        elif d == tomorrow:
            date_range_str.append(f"{d.strftime('%Y-%m-%d')} {day_name} (Tomorrow)")
        else:
            date_range_str.append(f"{d.strftime('%Y-%m-%d')} {day_name}")
    
    print(f"Data truncated: Kept {len(truncated_df)} events, filtered out {num_filtered} events")
    print(f"Date range: {', '.join(date_range_str)}")
    
    return truncated_df

# 🔹 Process and Generate Forex Signals
def process_cpi_data(df):
    # Filter only relevant CPI events
    cpi_events = df[df['event'].str.contains('CPI', case=False, na=False)]
    
    if cpi_events.empty:
        print("No CPI data found in the JSON file!")
        return pd.DataFrame()
    
    # Clean and convert the previous values
    def clean_numeric(value):
        if pd.isna(value) or value is None:
            return None
        
        # Convert to string if it's not already
        if not isinstance(value, str):
            return value
        
        # Clean the value - remove %, €, M, B, K symbols and spaces
        cleaned = value.replace('%', '').replace('€', '').replace('$', '')\
                      .replace('M', '').replace('B', '').replace('K', '')\
                      .replace(' ', '')
                      
        try:
            # Convert to float - if it has % sign, divide by 100
            numeric_value = float(cleaned)
            if '%' in value:
                numeric_value /= 100
            return numeric_value
        except (ValueError, TypeError):
            # Return None if conversion fails
            print(f"Warning: Could not convert '{value}' to numeric")
            return None
    
    cpi_events['previous_numeric'] = cpi_events['previous'].apply(clean_numeric)
    
    # Drop rows with missing previous values
    cpi_events = cpi_events.dropna(subset=['previous_numeric'])
    
    # Calculate change (if enough data points)
    if len(cpi_events) > 1:
        cpi_events = cpi_events.sort_values('date')
        cpi_events['change'] = cpi_events['previous_numeric'].pct_change()
    else:
        # If only one data point, can't calculate change
        cpi_events['change'] = 0

    # Define interest rate (Can be dynamic)
    interest_rate = 3.5  

    # Generate Forex Signal
    def forex_signal(row):
        if pd.isna(row["change"]):
            return "⚠️ INSUFFICIENT DATA"
            
        if row["change"] > 0 and interest_rate >= 3.5:
            return "🔹 STRONG BUY EUR"
        elif row["change"] < 0 and interest_rate < 2.0:
            return "🔹 STRONG SELL EUR"
        elif row["change"] > 0:
            return "🔹 BUY EUR"
        else:
            return "🔹 SELL EUR"

    cpi_events["signal"] = cpi_events.apply(forex_signal, axis=1)
    return cpi_events

# 🔹 Display Signals in a Formatted Output
def display_signals(df):
    if df.empty:
        print("\n❌ No signals could be generated - check your data source")
        return
        
    print("\n📊 Forex Trading Signals 📊\n")
    
    # Get today's date for comparison
    today = pd.Timestamp.today().normalize()
    tomorrow = today + pd.Timedelta(days=1)
    yesterday = today - pd.Timedelta(days=1)
    
    for _, row in df.iterrows():
        # Format date with weekday and special labels (Today/Tomorrow/Yesterday)
        date_obj = pd.to_datetime(row['date'])
        weekday = date_obj.strftime('%A')  # Full weekday name
        
        # Add friendly label if it's a notable date
        date_label = ""
        if date_obj.normalize() == today:
            date_label = " (Today)"
        elif date_obj.normalize() == tomorrow:
            date_label = " (Tomorrow)"
        elif date_obj.normalize() == yesterday:
            date_label = " (Yesterday)"
            
        formatted_date = f"{date_obj.strftime('%Y-%m-%d')} {weekday}{date_label}"
        
        print(f"📅 Date: {formatted_date} | 🕒 Time: {row['time'] if 'time' in row and not pd.isna(row['time']) else 'N/A'} | 🌍 Country: {row['country']}")
        print(f"📈 Event: {row['event']}")
        
        # Format change as percentage if available
        change_str = f"{row['change']:.2%}" if not pd.isna(row['change']) else "N/A"
        print(f"📊 CPI Change: {change_str}")
        
        print(f"💹 Signal: {row['signal']}\n")
        print("=" * 50)

# 🔹 Main Function
def main():
    file_path = "data.json"  # JSON file with scraped data
    df = load_cpi_data(file_path)  # Load data
    
    if df.empty:
        print("No data found! Please check your JSON file.")
        return
        
    # Truncate data to relevant date range (2 days before, today, and tomorrow)
    df = truncate_data(df, days_before=2, include_today=True, include_tomorrow=True)
    
    if df.empty:
        print("No data found in the specified date range!")
        return
    
    df = process_cpi_data(df)  # Process and generate signals
    display_signals(df)  # Show formatted output

# 🔹 Run the Script
if __name__ == "__main__":
    main()