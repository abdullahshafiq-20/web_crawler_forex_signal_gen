def transform_economic_events(events_data):
    """
    Transform raw MongoDB events data into a clean response format
    
    Args:
        events_data (list): Raw events data from MongoDB
        
    Returns:
        dict: Formatted response with transformed events data
    """
    transformed_data = []
    
    for event in events_data:
        # Extract only the required fields
        transformed_event = {
            "date": event.get("date"),
            "time": event.get("time"),
            "country": event.get("country"),
            "event": event.get("event"),
            "impact": event.get("impact"),
            "actual": event.get("actual"),
            "forecast": event.get("forecast"),
            "previous": event.get("previous"),
            "source": event.get("source")
        }
        transformed_data.append(transformed_event)
    
    return {
        "status": "success",
        "data": transformed_data
    }