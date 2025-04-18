import pymongo
from pymongo import MongoClient
from datetime import datetime
import pytz
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import re
import json
from bson import ObjectId

# Load environment variables from .env file
load_dotenv()

# Add JSONEncoder class to handle MongoDB ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

class EconomicCalendarDB:
    def __init__(self):
        """Initialize MongoDB connection using environment variables."""
        mongodb_uri = os.getenv("URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "forex_scraper")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.events = self.db.economic_events
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for efficient querying."""
        # Create a unique index on eventId to avoid duplicates
        self.events.create_index("eventId", unique=True)
        
        # Create indexes for common query patterns
        self.events.create_index("date")
        self.events.create_index("country")
        self.events.create_index("source")
        self.events.create_index([("date", pymongo.ASCENDING), ("time", pymongo.ASCENDING)])
        self.events.create_index([("date", pymongo.ASCENDING), ("impact", pymongo.ASCENDING)])
    
    def _convert_time_to_iso(self, date_str: str, time_str: Optional[str]) -> Optional[datetime]:
        """Convert date string and time string to ISO datetime."""
        if not date_str:
            return None
            
        try:
            # Handle case where time is not available
            if not time_str or time_str in ["All Day", "Tentative"]:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj
            
            # Clean time string (remove any non-numeric or colon characters)
            time_str = re.sub(r'[^0-9:]', '', time_str)
            
            # Handle cases where time might be incomplete
            if ":" not in time_str:
                if len(time_str) <= 2:
                    time_str = f"{time_str}:00"
                else:
                    # Try to split into hours and minutes
                    time_str = f"{time_str[:-2]}:{time_str[-2:]}"
                    
            # Create ISO datetime
            datetime_str = f"{date_str} {time_str}"
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
        except Exception as e:
            print(f"Error converting time: {str(e)} for date '{date_str}' and time '{time_str}'")
            return None
    
    def _normalize_impact(self, impact: Optional[str]) -> Optional[str]:
        """Normalize impact values from different sources."""
        if not impact:
            return None
            
        impact = impact.lower()
        
        # Map various impact terms to standard values
        if impact in ["high", "h", "3", "red"]:
            return "high"
        elif impact in ["medium", "m", "med", "2", "orange", "ora"]:
            return "medium"
        elif impact in ["low", "l", "1", "yellow", "yel"]:
            return "low"
        return impact
    
    def save_events(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save events to database with upsert to avoid duplicates.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with counts of created and updated records
        """
        created = 0
        updated = 0
        
        for event in events:
            # Skip invalid events
            if not event.get("date") or not event.get("event") or not event.get("country"):
                continue
                
            # Create a unique ID for the event
            event_time = event.get("time", "00:00")
            event_id = f"{event['date']}_{event_time}_{event['country']}_{event['event']}"
            
            # Create ISO timestamp if possible
            timestamp = self._convert_time_to_iso(event.get("date"), event.get("time"))
            
            # Normalize impact value
            normalized_impact = self._normalize_impact(event.get("impact"))
            
            # Prepare document for upsert
            document = {
                "eventId": event_id,
                "date": event.get("date"),
                "time": event.get("time"),
                "country": event.get("country"),
                "event": event.get("event"),
                "impact": normalized_impact,
                "actual": event.get("actual"),
                "forecast": event.get("forecast"),
                "previous": event.get("previous"),
                "source": event.get("source"),
                "sourceData": event,  # Store original data
                "updatedAt": datetime.now()
            }
            
            # Add timestamp if available
            if timestamp:
                document["timestamp"] = timestamp
            
            # Upsert the document
            result = self.events.update_one(
                {"eventId": event_id},
                {
                    "$set": document,
                    "$setOnInsert": {"createdAt": datetime.now()}
                },
                upsert=True
            )
            
            if result.upserted_id:
                created += 1
            elif result.modified_count > 0:
                updated += 1
        
        return {"created": created, "updated": updated}
    
    def get_events(self, 
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  countries: Optional[List[str]] = None,
                  impact: Optional[List[str]] = None,
                  sources: Optional[List[str]] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query events with various filters.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            countries: List of country/currency codes to filter
            impact: List of impact levels to filter ("high", "medium", "low")
            sources: List of sources to include
            limit: Maximum number of records to return
            
        Returns:
            List of event dictionaries
        """
        query = {}
        
        # Add date range filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["date"] = date_filter
        
        # Add country filter
        if countries:
            query["country"] = {"$in": countries}
        
        # Add impact filter
        if impact:
            query["impact"] = {"$in": impact}
        
        # Add source filter
        if sources:
            query["source"] = {"$in": sources}
        
        # Execute query
        cursor = self.events.find(
            query,
            {"sourceData": 0}  # Exclude the sourceData field to reduce response size
        ).sort([("date", pymongo.ASCENDING), ("time", pymongo.ASCENDING)]).limit(limit)
        
        return list(cursor)
    
class SignalDB:
    def __init__(self):
        """Initialize MongoDB connection for signals."""
        mongodb_uri = os.getenv("URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "forex_scraper")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.signals = self.db.signals
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for efficient querying."""
        # Create a unique index on signalId to avoid duplicates
        self.signals.create_index("signalId", unique=True)
        
        # Create indexes for common query patterns
        self.signals.create_index("date")
        self.signals.create_index("pair")
        self.signals.create_index("direction")
        self.signals.create_index("strength")
        self.signals.create_index("confidence")
        self.signals.create_index("rationale")
        self.signals.create_index("impact")
        self.signals.create_index([("date", pymongo.ASCENDING), ("pair", pymongo.ASCENDING)])
        self.signals.create_index([("date", pymongo.ASCENDING), ("direction", pymongo.ASCENDING)])

    
    def save_signals(self, signals_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save complete signals data (including market summary and multiple signals)
        If signals for the same date already exist, update them instead of creating a new document.
        
        Args:
            signals_data: Dictionary containing market summary and signals array
            
        Returns:
            Dictionary with result information
        """
        try:
            # Make sure we have a date field
            if 'date' not in signals_data:
                signals_data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            current_date = signals_data['date']
            
            # Add timestamps
            signals_data['timestamp'] = datetime.now()
            signals_data['updatedAt'] = datetime.now()
            
            # Check if signals for this date already exist
            existing_signal = self.signals.find_one({"date": current_date})
            
            if existing_signal:
                # Update existing document
                result = self.signals.update_one(
                    {"date": current_date},
                    {
                        "$set": {
                            "market_summary": signals_data.get("market_summary", ""),
                            "signals": signals_data.get("signals", []),
                            "timestamp": datetime.now(),
                            "updatedAt": datetime.now()
                        }
                    }
                )
                
                return {
                    "success": True,
                    "updated": True,
                    "message": f"Signals data for {current_date} updated successfully"
                }
            else:
                # Generate a unique signalId for new document
                signals_data['signalId'] = f"signals_{current_date}_{datetime.now().strftime('%H%M%S')}"
                signals_data['createdAt'] = datetime.now()
                
                # Insert the data as new document
                result = self.signals.insert_one(signals_data)
                
                return {
                    "success": True,
                    "inserted_id": str(result.inserted_id),
                    "message": f"New signals data for {current_date} saved successfully"
                }
                
        except Exception as e:
            # Return error information
            return {
                "success": False,
                "message": f"Failed to save signals data: {str(e)}"
            }

    def get_signals(self,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  pairs: Optional[List[str]] = None,
                  directions: Optional[List[str]] = None,
                  strengths: Optional[List[str]] = None,
                  confidences: Optional[List[str]] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query signals with various filters.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            pairs: List of currency pairs to filter
            directions: List of directions to filter ("BUY", "SELL")
            strengths: List of strength levels to filter ("HIGH", "MEDIUM", "LOW")
            confidences: List of confidence levels to filter (0-100%)
            limit: Maximum number of records to return
            
        Returns:
            List of signal dictionaries
        """
        query = {}
        
        # Add date range filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["date"] = date_filter
        
        # Add pair filter
        if pairs:
            query["pair"] = {"$in": pairs}
        
        # Add direction filter
        if directions:
            query["direction"] = {"$in": directions}
        
        # Add strength filter
        if strengths:
            query["strength"] = {"$in": strengths}
        
        # Add confidence filter
        if confidences:
            query["confidence"] = {"$in": confidences}
        
        # Execute query
        cursor = self.signals.find(
            query,
            {"signalId": 0}  # Exclude the signalId field to reduce response size
        ).sort([("date", pymongo.ASCENDING), ("pair", pymongo.ASCENDING)]).limit(limit)
        
        return list(cursor)
    

    def get_today_signals(self) -> List[Dict[str, Any]]:
        """Fetch signals for today."""
        today = datetime.now(pytz.timezone('UTC')).strftime('%Y-%m-%d')
        return self.get_signals(start_date=today, end_date=today)
