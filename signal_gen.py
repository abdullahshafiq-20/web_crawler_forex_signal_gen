import pandas as pd
import json
import datetime

# 🔹 Load Economic Data from JSON File
def load_economic_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        df = pd.DataFrame(data)
        
        if df.empty:
            print(f"Warning: No data found in {file_path}")
            return pd.DataFrame()
            
        # Show summary of available events for debugging
        if 'event' in df.columns:
            event_counts = df['event'].value_counts()
            print(f"Found {len(event_counts)} different event types")
            print(f"Top events: {', '.join(event_counts.index[:5])}")
                
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
def process_economic_data(df):
    if df.empty:
        print("No economic data found in the JSON file!")
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
    
    # Process all events with numeric previous values
    df['previous_numeric'] = df['previous'].apply(clean_numeric)
    
    # Drop rows with missing previous values
    processed_df = df.dropna(subset=['previous_numeric'])
    
    # Group by country and event to calculate changes within same event types
    event_groups = processed_df.groupby(['country', 'event'])
    
    result_dfs = []
    
    for (country, event), group_df in event_groups:
        if len(group_df) > 1:
            temp_df = group_df.sort_values('date')
            temp_df['change'] = temp_df['previous_numeric'].pct_change()
        else:
            # If only one data point, can't calculate change
            temp_df = group_df.copy()
            temp_df['change'] = None
        
        result_dfs.append(temp_df)
    
    if not result_dfs:
        return pd.DataFrame()
    
    # Combine all processed groups back into one dataframe
    processed_df = pd.concat(result_dfs)
    
    # Generate Forex Signal by analyzing event impact and change direction
    def forex_signal(row):
        if pd.isna(row["change"]):
            return "⚠️ INSUFFICIENT DATA"

        # Classify event type
        event_lower = row["event"].lower()
        country = row["country"]
        change = row["change"]
        
        # Default impact direction (whether increase is positive)
        increase_is_positive = True
        
        # Identify common economic indicators and their impact direction
        if any(term in event_lower for term in ["inflation", "cpi", "ppi"]):
            increase_is_positive = False  # Higher inflation generally negative
        elif any(term in event_lower for term in ["unemployment", "jobless"]):
            increase_is_positive = False  # Higher unemployment generally negative
        elif any(term in event_lower for term in ["gdp", "growth", "production", "pmi", "manufacturing", "sales"]):
            increase_is_positive = True   # Higher growth generally positive
        elif "rate" in event_lower and any(term in event_lower for term in ["interest", "central", "bank"]):
            # Interest rate impact depends on economic context - assuming higher rates = stronger currency
            increase_is_positive = True

        # Generate signal based on change direction and impact type
        if (change > 0 and increase_is_positive) or (change < 0 and not increase_is_positive):
            return f"🔹 BUY {country}"
        else:
            return f"🔹 SELL {country}"

    processed_df["signal"] = processed_df.apply(forex_signal, axis=1)
    return processed_df

# 🔹 Display Signals in a Formatted Output
def display_signals(df):
    if df.empty:
        print("\n❌ No signals could be generated - check your data source")
        return
        
    print("\n📊 Economic Trading Signals 📊\n")
    
    # Get today's date for comparison
    today = pd.Timestamp.today().normalize()
    tomorrow = today + pd.Timedelta(days=1)
    yesterday = today - pd.Timedelta(days=1)
    
    # Group by date for better readability
    df['date'] = pd.to_datetime(df['date'])
    date_groups = df.groupby(df['date'].dt.normalize())
    
    for date, group in sorted(date_groups):
        # Format date with weekday and special labels
        weekday = date.strftime('%A')
        date_label = ""
        if date == today:
            date_label = " (Today)"
        elif date == tomorrow:
            date_label = " (Tomorrow)"
        elif date == yesterday:
            date_label = " (Yesterday)"
            
        formatted_date = f"{date.strftime('%Y-%m-%d')} {weekday}{date_label}"
        print(f"\n📅 {formatted_date}")
        print("=" * 50)
        
        # Sort events by time if available
        if 'time' in group.columns:
            group = group.sort_values('time')
        
        for _, row in group.iterrows():
            print(f"🕒 Time: {row['time'] if 'time' in row and not pd.isna(row['time']) else 'N/A'} | 🌍 Country: {row['country']}")
            print(f"📈 Event: {row['event']}")
            
            # Format change as percentage if available
            change_str = f"{row['change']:.2%}" if not pd.isna(row['change']) else "N/A"
            print(f"📊 Change: {change_str}")
            
            print(f"💹 Signal: {row['signal']}\n")
            print("-" * 40)

# 🔹 Main Function
def main():
    file_path = "data.json"  # JSON file with scraped data
    df = load_economic_data(file_path)  # Load data
    
    if df.empty:
        print("No data found! Please check your JSON file.")
        return
        
    # Truncate data to relevant date range (2 days before, today, and tomorrow)
    df = truncate_data(df, days_before=2, include_today=True, include_tomorrow=True)
    
    if df.empty:
        print("No data found in the specified date range!")
        return
    
    df = process_economic_data(df)  # Process and generate signals
    display_signals(df)  # Show formatted output

# 🔹 Run the Script
if __name__ == "__main__":
    main()