from datetime import datetime
from bson import ObjectId

def extract_source_data(economic_events):
    events_for_ai = []
    
    # If it's a single document rather than a list
    if not isinstance(economic_events, list):
        economic_events = [economic_events]
    
    for event in economic_events:
        # Convert to dictionary if it's a MongoDB document
        if hasattr(event, 'to_dict'):
            event = event.to_dict()
        elif hasattr(event, '__getitem__') and not isinstance(event, dict):
            # Some MongoDB libraries return document-like objects
            try:
                event = dict(event)
            except:
                print(f"Couldn't convert event to dictionary: {type(event)}")
                continue
        
        # Extract only the specific fields you need
        clean_event_data = {
            "actual": event.get("actual", ""),
            "country": event.get("country", ""),
            "date": event.get("date", ""),
            "event": event.get("event", ""),
            "forecast": event.get("forecast", ""),
            "impact": event.get("impact", ""),
            "previous": event.get("previous", ""),
            "source": event.get("source", ""),
            "time": event.get("time", ""),
        }
        
        events_for_ai.append(clean_event_data)
    
    print(f"Total events processed: {len(economic_events)}")
    print(f"Events extracted: {len(events_for_ai)}")
    return events_for_ai