from fastapi import FastAPI, Query
from scraper import scrape_cashback_forex
from scraper import forex_factory_scraper
from utils.getToday import get_today_data
from utils.getSourceData import extract_source_data
from signal_generator import analyze_with_ai, clean_json_response, analyze_signal_gemeni
import concurrent.futures
from typing import List, Optional
from db import EconomicCalendarDB, SignalDB, JSONEncoder
from datetime import datetime
import os
import json
from bson.json_util import dumps

app = FastAPI()
calendar_db = EconomicCalendarDB()
signals_db = SignalDB()

@app.get("/scrape/cashbackforex")
async def scrape():
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data = await app.state.loop.run_in_executor(
                executor, lambda: scrape_cashback_forex())
            
            events = json.loads(data)
            # Filter today's data
            with open('events.json', 'w') as f:
                json.dump(events, f, indent=4)

            todays_data = get_today_data(events)
            with open('todays_data.json', 'w') as f:
                json.dump(todays_data, f, indent=4)
            result = calendar_db.save_events(todays_data)
            return {
                "status": "success", 
                "data": todays_data, 
                "db_result": result
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "Scraping failed",
            "error_type": type(e).__name__,
            "details": str(e)
        }
    
@app.get("/scrape/forexfactory")
async def scrape():
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data = await app.state.loop.run_in_executor(
                executor, lambda: forex_factory_scraper())
            
            events = json.loads(data)
            # Filter today's data
            with open('events.json', 'w') as f:
                json.dump(events, f, indent=4)
            # Filter today's data
            todays_data = get_today_data(events)
            print("Tidays Data", todays_data)
            result = calendar_db.save_events(todays_data)
            return {
                "status": "success", 
                "data": todays_data, 
                "db_result": result
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "Scraping failed",
            "error_type": type(e).__name__,
            "details": str(e)
        }
    

@app.get("/generate-signals")
async def generate_signals():
    try:
        # Fetch economic events from the database
        economic_events = calendar_db.get_events()

        # print(economic_events)
        serialized_events = JSONEncoder().encode(economic_events)
        events = json.loads(serialized_events)

        
        events_for_ai = extract_source_data(events)
        # print(f"Events for AI: {events_for_ai}")
        
                
        with concurrent.futures.ThreadPoolExecutor() as executor:
            ai_response = await app.state.loop.run_in_executor(
                executor, lambda: analyze_signal_gemeni(events_for_ai))
                
        if not ai_response:
            return {
                "status": "error",
                "message": "Failed to get response from AI"
            }
        
        # print (f"AI Response: {ai_response}")

 
        cleaned_content = clean_json_response(ai_response)

        print(f"Cleaned Content: {cleaned_content}")

        
        try:
            # Parse JSON
            analysis_json = json.loads(cleaned_content)
            
            # Validate the JSON structure
            if 'signals' not in analysis_json or not isinstance(analysis_json['signals'], list):
                raise ValueError("Invalid JSON structure: 'signals' key is missing or not a list")
                
            # Add timestamp and date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Use save_signals method instead of save_signal
            # This handles complete signal data with market summary and signals array
            signals_data = {
                "market_summary": analysis_json.get("market_summary", ""),
                "signals": analysis_json.get("signals", []),
                "date": current_date,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to MongoDB using the SignalDB class
            result = signals_db.save_signals(signals_data)
            
            # Return a JSON-serializable response
            return {
                "status": "success",
                "message": "Signals generated and saved",
                "db_result": result,
                "signals": {
                    "market_summary": analysis_json.get("market_summary", ""),
                    "signals": analysis_json.get("signals", []),
                    "date": current_date,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": "Failed to parse AI response as JSON",
                "error": str(e),
                "raw_content": ai_response,
                "cleaned_content": cleaned_content
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": "Signal generation failed",
            "error_type": type(e).__name__,
            "details": str(e)
        }

@app.get("/signals")
async def get_signals(date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD format)")):
    try:
        # Get signals using the SignalDB class
        if date:
            signals = signals_db.get_signals(start_date=date, end_date=date)
        else:
            signals = signals_db.get_today_signals()
            
        # Convert MongoDB objects for JSON response using JSON encoder
        serialized_signals = JSONEncoder().encode(signals)
        signals_response = json.loads(serialized_signals)
        
        return {
            "status": "success",
            "count": len(signals),
            "signals": signals_response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to retrieve signals",
            "error_type": type(e).__name__,
            "details": str(e)
        }

@app.get("/scrape/all")
async def scrape_all():
    try:
        results = {}
        errors = {}
        
        # Use concurrent execution to run both scrapers in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Start both scraping tasks
            cashback_future = executor.submit(scrape_cashback_forex)
            forexfactory_future = executor.submit(forex_factory_scraper)
            
            # Process Cashback Forex data
            try:
                cashback_data = cashback_future.result()
                cashback_events = json.loads(cashback_data)
                cashback_today = get_today_data(cashback_events)
                cashback_result = calendar_db.save_events(cashback_today)
                results["cashbackforex"] = {
                    "status": "success", 
                    "data_count": len(cashback_today),
                    "db_result": cashback_result
                }
            except Exception as e:
                errors["cashbackforex"] = {
                    "status": "error",
                    "message": "Scraping failed",
                    "error_type": type(e).__name__,
                    "details": str(e)
                }
            
            # Process Forex Factory data
            try:
                forexfactory_data = forexfactory_future.result()
                forexfactory_events = json.loads(forexfactory_data)
                forexfactory_today = get_today_data(forexfactory_events)
                forexfactory_result = calendar_db.save_events(forexfactory_today)
                results["forexfactory"] = {
                    "status": "success", 
                    "data_count": len(forexfactory_today),
                    "db_result": forexfactory_result
                }
            except Exception as e:
                errors["forexfactory"] = {
                    "status": "error",
                    "message": "Scraping failed",
                    "error_type": type(e).__name__,
                    "details": str(e)
                }
        
        # Combine all scraped events
        all_events = calendar_db.get_events()
        
        return {
            "status": "complete" if not errors else "partial",
            "results": results,
            "errors": errors if errors else None,
            "total_events_saved": len(all_events),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Combined scraping operation failed",
            "error_type": type(e).__name__,
            "details": str(e)
        }


@app.on_event("startup")
async def startup_event():
    import asyncio
    app.state.loop = asyncio.get_running_loop()