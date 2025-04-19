# Web Crawler & Economic Event Signal Generator

![Main image](https://res.cloudinary.com/dkb1rdtmv/image/upload/v1745091536/Screenshot_2025-04-20_002008_gvhsdn.png)
---

## Motivation
*In the rapidly evolving financial sector, access to real-time, accurate economic event data is essential for informed trading decisions. This project is motivated by the need to automate the extraction, aggregation, and analysis of global economic events using advanced web scraping and networking techniques, ensuring timely delivery of actionable insights to traders and analysts.*

## Overview

### Significance
- Automates the collection and synchronization of economic event data from multiple online sources.
- Uses robust networking and scraping technologies (Selenium, BeautifulSoup) for dynamic content.
- Provides reliable, up-to-date data for financial analysis and trading signal generation.

### Description
- Distributed web scraping and data analysis platform.
- Backend (Python, FastAPI) uses Selenium and BeautifulSoup to scrape economic calendars (e.g., CashbackForex, ForexFactory).
- Scraped data is processed, stored in MongoDB, and served via REST APIs.
- Frontend (React) visualizes data and signals.
- Networking: concurrent scraping, async APIs, secure API key management.

### Background
- Selenium for dynamic web scraping ([Selenium Docs](https://www.selenium.dev/documentation/))
- Selenium Stealth, WebDriver Manager for anti-bot evasion
- FastAPI for backend ([FastAPI Docs](https://fastapi.tiangolo.com/))
- MongoDB for data storage ([MongoDB Docs](https://www.mongodb.com/docs/))
- BeautifulSoup for HTML parsing ([BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/))
- Related: [Investing.com Economic Calendar](https://www.investing.com/economic-calendar/), [Forex Factory](https://www.forexfactory.com/calendar)
- Networking: REST, CORS, concurrent futures


## Features / Scope / Modules

1. **Advanced Web Scraping with Selenium**
   - Scrapes dynamic economic event data from multiple sources, bypassing anti-bot protections using Selenium Stealth.
2. **Concurrent and Distributed Scraping**
   - Uses Python’s concurrent.futures for parallel scraping, improving speed and reliability.
3. **Robust Networking Layer**
   - FastAPI-based REST endpoints for data access, with CORS and secure API key management.
4. **Automated Data Cleaning and Transformation**
   - Cleans, deduplicates, and normalizes scraped data for consistency.
5. **Real-Time Data Synchronization**
   - Ensures all users and services have access to the latest data via efficient networking.
6. **AI-Powered Signal Generation**
   - Integrates with OpenRouter and Gemini APIs for automated trading signal analysis.
7. **User Dashboard**
   - React frontend for visualization and interaction with economic data and signals.
8. **Scalable and Secure Architecture**
   - Modular backend, environment-based secrets, and scalable database design.

---


## Feasibility

- **Technical:** Uses proven tools (Selenium, FastAPI, MongoDB, React). Handles anti-bot and website changes with Selenium Stealth and modular code.
- **Economic:** Open-source stack minimizes costs. Cloud/API usage may incur minor expenses.
- **Schedule:** 10-week plan with parallel development and buffer for issues.

---

## Hardware and Software Requirements

- **Hardware:** Standard PC/laptop, stable internet, optional cloud server.
- **Software:**
  - Python 3.11+, Node.js, MongoDB
  - Selenium, webdriver-manager, selenium-stealth, requests, beautifulsoup4, fastapi, uvicorn, pymongo, dotenv
  - React, Vite, Tailwind CSS
  - AI API access (OpenRouter, Gemini)
  - Git, VS Code

---

## System Architecture

- Data sources (websites/APIs)
- Selenium-based scraper modules
- Backend API (FastAPI)
- Database (MongoDB)
- AI signal generator
- Frontend (React + Shadcn)
- Networking flows (REST, concurrent scraping, CORS)

![logo](https://res.cloudinary.com/dkb1rdtmv/image/upload/v1745092521/mermaid-diagram-2025-04-20-005507_wa543w.png)
---

## How to Run

1. **Clone the repository**
2. **Install backend dependencies:**
   - `cd server && pip install -r requirements.txt`
3. **Install frontend dependencies:**
   - `cd client && npm install`
4. **Set up environment variables:**
   - See `server/.env` for API keys and MongoDB URI
5. **Run the backend:**
   - `cd server && uvicorn main:app --reload`
6. **Run the frontend:**
   - `cd client && npm run dev`

---

## License

MIT License
