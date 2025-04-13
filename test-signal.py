import json
import re
import sys
from pprint import pprint
from datetime import datetime

def parse_value(value):
    """
    Parses a string value that may include currency symbols, units (B, M, K), or % signs.
    Converts the value to a float.
    """
    if value is None:
        return None
    if isinstance(value, str):
        # Clean up the string
        value = value.strip().upper().replace(',', '')
        
        # Handle percentage values
        is_percentage = False
        if '%' in value:
            is_percentage = True
            value = value.replace('%', '')
        
        # Extract the currency code if present (typically 3 letters at the beginning)
        currency_match = re.match(r'^([A-Z]{3})(.*)', value)
        if currency_match:
            # Remove the currency code
            value = currency_match.group(2)
        else:
            # Try to strip any other currency symbols or codes
            value = re.sub(r'(USD|EUR|GBP|JPY|CNY|THB|ILS|CAD|AUD|NZD|CHF|INR|\$|€|£|¥)', '', value)
        
        # Handle multipliers (B=billion, M=million, K=thousand)
        if 'B' in value:
            value = value.replace('B', '')
            try:
                return float(value) * 1000000000
            except (ValueError, TypeError):
                return None
        elif 'M' in value:
            value = value.replace('M', '')
            try:
                return float(value) * 1000000
            except (ValueError, TypeError):
                return None
        elif 'K' in value:
            value = value.replace('K', '')
            try:
                return float(value) * 1000
            except (ValueError, TypeError):
                return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def calculate_diff(actual, compare_to):
    """
    Calculates the percentage difference between actual and a comparison value.
    """
    if actual is None or compare_to is None or compare_to == 0:
        return 0
    try:
        return ((actual - compare_to) / abs(compare_to)) * 100
    except (ZeroDivisionError, TypeError):
        return 0

def evaluate_signal(impact, diff_forecast, diff_previous, actual_value=None, forecast_value=None):
    """
    Evaluates the signal strength based on the impact rating and calculated percentage differences.
    Thresholds may be modified to fit your criteria.
    """
    # Define thresholds based on the impact level
    if impact == "high":
        threshold = (10, 3)
    elif impact == "medium":
        threshold = (7, 2)
    elif impact == "low":
        threshold = (3, 1)
    else:
        threshold = (5, 2)  # Default thresholds if impact is not specified
    
    # Additional check: if actual is present but forecast is missing, we should not generate a signal
    if actual_value is None or forecast_value is None:
        return "No Signal"
    
    # Evaluate signal based on thresholds
    if diff_forecast > threshold[0] and diff_previous > threshold[0]:
        return "Strong Buy"
    elif diff_forecast > threshold[1]:
        return "Medium Buy"
    elif diff_forecast < -threshold[0] and diff_previous < -threshold[0]:
        return "Strong Sell"
    elif diff_forecast < -threshold[1]:
        return "Medium Sell"
    else:
        return "Neutral"

def generate_predictive_signal(impact, forecast, previous):
    """
    Generates predictive signals for upcoming events based on forecast and previous values.
    """
    # Only generate predictive signals if both forecast and previous are available
    if forecast is None or previous is None:
        return "No Prediction"
    
    diff = calculate_diff(forecast, previous)
    
    # Use different thresholds for predictive signals
    if impact == "high":
        threshold = 8
    elif impact == "medium":
        threshold = 5
    else:
        threshold = 3
    
    if diff > threshold:
        return "Potentially Bullish"
    elif diff < -threshold:
        return "Potentially Bearish"
    else:
        return "Likely Neutral"

def enhanced_signal(economic_signal, technical_indicators=None):
    """
    Enhances economic signals with technical analysis data.
    """
    if technical_indicators is None or not isinstance(technical_indicators, dict):
        return economic_signal
        
    # If economic and technical signals align, generate a stronger signal
    if economic_signal == "Strong Buy" and technical_indicators.get("trend") == "Bullish":
        return "High Confidence Buy"
    elif economic_signal == "Medium Buy" and technical_indicators.get("trend") == "Bullish":
        return "Confident Buy"
    elif economic_signal == "Strong Sell" and technical_indicators.get("trend") == "Bearish":
        return "High Confidence Sell"
    elif economic_signal == "Medium Sell" and technical_indicators.get("trend") == "Bearish":
        return "Confident Sell"
    else:
        return economic_signal  # Default to economic signal

def sentiment_enhanced_signal(basic_signal, event_name, sentiment_score=None):
    """
    Enhances signals with sentiment analysis.
    """
    # Mock sentiment analysis based on event name if no sentiment score is provided
    if sentiment_score is None:
        # This is a very simplistic approach - in real use, you'd use actual sentiment analysis
        positive_keywords = ["growth", "increase", "expand", "gain", "positive", "rise", "improve", "recovery"]
        negative_keywords = ["contraction", "decline", "decrease", "drop", "negative", "fall", "worsen", "recession"]
        
        if event_name:
            event_lower = event_name.lower()
            positive_matches = sum(1 for word in positive_keywords if word in event_lower)
            negative_matches = sum(1 for word in negative_keywords if word in event_lower)
            
            if positive_matches > negative_matches:
                sentiment_score = 0.7  # Positive sentiment
            elif negative_matches > positive_matches:
                sentiment_score = -0.7  # Negative sentiment
            else:
                sentiment_score = 0  # Neutral sentiment
        else:
            return basic_signal
    
    if basic_signal == "No Signal" and sentiment_score > 0.6:
        return "Sentiment Buy"
    elif basic_signal == "No Signal" and sentiment_score < -0.6:
        return "Sentiment Sell"
    elif abs(sentiment_score) > 0.8:  # Very strong sentiment could override
        return "Strong Sentiment " + ("Buy" if sentiment_score > 0 else "Sell")
    else:
        return basic_signal

def volatility_signal(event_impact, is_actual_available):
    """
    Identifies potential volatility around high-impact events.
    """
    if not is_actual_available and event_impact == "high":
        return "Potential Volatility"
    return "No Volatility Expected"

def calculate_confidence(base_signal, enhanced_signal, sentiment_signal):
    """
    Calculates confidence level in the signal.
    """
    # Base confidence
    if "Strong" in base_signal:
        base_confidence = 0.8
    elif "Medium" in base_signal:
        base_confidence = 0.6
    elif "Neutral" in base_signal:
        base_confidence = 0.5
    else:
        base_confidence = 0.3
    
    # Check if signals are consistent
    signals_match = False
    if ("Buy" in base_signal and "Buy" in enhanced_signal) or \
       ("Sell" in base_signal and "Sell" in enhanced_signal) or \
       (base_signal == enhanced_signal):
        signals_match = True
        
    # Adjust confidence
    if signals_match:
        enhanced_confidence = base_confidence + 0.1
    else:
        enhanced_confidence = base_confidence - 0.1
    
    # Cap at 0.95 (never 100% confident)
    confidence = min(enhanced_confidence, 0.95)
    
    return round(confidence, 2)

def format_date(date_str, time_str=None):
    """
    Formats the date and time strings into a consistent format.
    """
    if not date_str:
        return None
    
    # Try to parse the date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        
        # Add time if available
        if time_str:
            # Handle various time formats
            time_str = time_str.replace('am', ' AM').replace('pm', ' PM')
            
            # Try different time formats
            time_formats = ["%H:%M", "%I:%M %p", "%I:%M%p"]
            for fmt in time_formats:
                try:
                    time_obj = datetime.strptime(time_str, fmt)
                    return f"{formatted_date} {time_obj.strftime('%H:%M')}"
                except ValueError:
                    continue
                
        return formatted_date
    except ValueError:
        return date_str

def generate_signals(data, technical_data=None, sentiment_data=None):
    """
    Processes the event data and generates enhanced signals based on:
    - Economic data (actual vs forecast vs previous)
    - Predictive signals for upcoming events
    - Technical indicators (if provided)
    - Sentiment analysis (if provided)
    - Volatility expectations
    
    Returns a list of events with comprehensive signal information.
    """
    signals = []

    for event in data:
        country = event.get('country')
        name = event.get('event')
        impact = (event.get('impact') or '').lower()
        actual = parse_value(event.get('actual'))
        forecast = parse_value(event.get('forecast'))
        previous = parse_value(event.get('previous'))
        
        # Format the date
        formatted_date = format_date(event.get('date'), event.get('time'))

        # Calculate differences if values are available
        diff_forecast = calculate_diff(actual, forecast)
        diff_previous = calculate_diff(actual, previous)
        
        # Generate basic economic signal
        base_signal = "No Signal"
        if actual is not None and forecast is not None:
            base_signal = evaluate_signal(impact, diff_forecast, diff_previous, actual, forecast)
        
        # For upcoming events with no actual data yet, generate predictive signal
        predictive_signal = "No Prediction"
        if actual is None and forecast is not None and previous is not None:
            predictive_signal = generate_predictive_signal(impact, forecast, previous)
        
        # Get technical indicators for this currency/country if available
        tech_indicators = None
        if technical_data and country in technical_data:
            tech_indicators = technical_data.get(country)
        
        # Enhance signal with technical analysis
        enhanced_signal_var = enhanced_signal(base_signal, tech_indicators)
        
        # Add sentiment analysis
        sentiment_score = None
        if sentiment_data and name in sentiment_data:
            sentiment_score = sentiment_data.get(name)
        
        final_signal = sentiment_enhanced_signal(enhanced_signal_var, name, sentiment_score)
        
        # Generate volatility expectation
        volatility = volatility_signal(impact, actual is not None)
        
        # Calculate confidence in the signal
        confidence = calculate_confidence(base_signal, enhanced_signal_var, final_signal)
        
        signals.append({
            "date": event.get("date"),
            "time": event.get("time"),
            "formatted_datetime": formatted_date,
            "country": country,
            "event": name,
            "impact": impact,
            "actual_raw": event.get("actual"),
            "forecast_raw": event.get("forecast"),
            "previous_raw": event.get("previous"),
            "actual": actual,
            "forecast": forecast, 
            "previous": previous,
            "base_signal": base_signal,
            "predictive_signal": predictive_signal,
            "enhanced_signal": enhanced_signal_var,
            "final_signal": final_signal,
            "volatility": volatility,
            "confidence": confidence,
            "diff_forecast_%": round(diff_forecast, 2) if diff_forecast else None,
            "diff_previous_%": round(diff_previous, 2) if diff_previous else None,
            "source": event.get("source")
        })

    return signals

def main():
    file_path = "data.json"
    output_path = "enhanced_signals.json"
    
    # Allow command line arguments for input and output files
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    # Mock technical analysis data - in a real system, you would import this from another source
    technical_data = {
        "USD": {"trend": "Bullish", "rsi": 65, "macd": "positive"},
        "EUR": {"trend": "Bearish", "rsi": 35, "macd": "negative"},
        "GBP": {"trend": "Neutral", "rsi": 50, "macd": "neutral"},
        "JPY": {"trend": "Bearish", "rsi": 30, "macd": "negative"},
        "CAD": {"trend": "Bullish", "rsi": 70, "macd": "positive"},
        "AUD": {"trend": "Neutral", "rsi": 45, "macd": "neutral"},
        "NZD": {"trend": "Bullish", "rsi": 68, "macd": "positive"}
    }
    
    # Generate enhanced signals with all available data
    signals = generate_signals(data)
    
    try:
        with open(output_path, 'w') as f:
            json.dump(signals, f, indent=4)
        print(f"Enhanced signals saved to {output_path}")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        sys.exit(1)
    
    # Print summary statistics
    buy_signals = [s for s in signals if "Buy" in s.get("final_signal", "")]
    sell_signals = [s for s in signals if "Sell" in s.get("final_signal", "")]
    neutral_signals = [s for s in signals if "Neutral" in s.get("final_signal", "")]
    no_signals = [s for s in signals if s.get("final_signal") == "No Signal"]
    predictive_signals = [s for s in signals if s.get("predictive_signal") != "No Prediction"]
    volatility_alerts = [s for s in signals if s.get("volatility") == "Potential Volatility"]
    
    print(f"\nGenerated {len(signals)} comprehensive signals:")
    print(f"- Buy Signals: {len(buy_signals)}")
    print(f"- Sell Signals: {len(sell_signals)}")
    print(f"- Neutral Signals: {len(neutral_signals)}")
    print(f"- No Signals: {len(no_signals)}")
    print(f"- Predictive Signals: {len(predictive_signals)}")
    print(f"- Volatility Alerts: {len(volatility_alerts)}")
    
    print("\nSignal Examples:")
    for signal_type in ["High Confidence Buy", "Confident Buy", "Strong Buy", "Medium Buy", 
                         "High Confidence Sell", "Confident Sell", "Strong Sell", "Medium Sell", 
                         "Neutral", "Potentially Bullish", "Potentially Bearish"]:
        examples = [s for s in signals if s.get("final_signal") == signal_type or s.get("predictive_signal") == signal_type][:2]
        if examples:
            print(f"\n{signal_type} Examples:")
            for example in examples:
                if "Potentially" in signal_type:
                    print(f"  {example.get('country')} - {example.get('event')}: " 
                          f"Forecast {example.get('forecast_raw')} vs Previous {example.get('previous_raw')}, "
                          f"Confidence: {example.get('confidence') * 100}%")
                else:
                    print(f"  {example.get('country')} - {example.get('event')}: " 
                          f"Actual {example.get('actual_raw')} vs Forecast {example.get('forecast_raw')}, "
                          f"Diff: {example.get('diff_forecast_%')}%, Confidence: {example.get('confidence') * 100}%")

if __name__ == "__main__":
    main()