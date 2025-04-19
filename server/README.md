# Web Crawler & Economic Event Signal Generator

## Motivation
*In the rapidly evolving financial sector, access to real-time, accurate economic event data is essential for informed trading decisions. This project is motivated by the need to automate the extraction, aggregation, and analysis of global economic events using advanced web scraping and networking techniques, ensuring timely delivery of actionable insights to traders and analysts.*

## Overview

### 2.1 Significance of the Project
This project addresses the challenge of collecting and synchronizing economic event data from multiple online sources, which is often scattered and inconsistently formatted. By leveraging robust networking and scraping technologies (notably Selenium for dynamic content), the system ensures reliable, up-to-date data for financial analysis and trading signal generation. The project’s significance lies in its automation, scalability, and potential to improve trading outcomes.

### 2.2 Description of the Project
The core idea is to build a distributed web scraping and data analysis platform. The backend (Python, FastAPI) uses Selenium and BeautifulSoup to scrape economic calendars from sites like CashbackForex and ForexFactory, handling dynamic content and anti-bot measures. Scraped data is processed, stored in MongoDB, and made available via REST APIs. The frontend (React) visualizes this data. Networking is central: the system uses concurrent scraping, asynchronous APIs, and secure environment-based API key management to ensure efficient, scalable, and secure data flow.

### 2.3 Background of the Project
- Selenium for dynamic web scraping ([Selenium Docs](https://www.selenium.dev/documentation/))
- Selenium Stealth and WebDriver Manager for anti-bot evasion and driver management
- FastAPI for high-performance backend APIs ([FastAPI Docs](https://fastapi.tiangolo.com/))
- MongoDB for flexible, scalable data storage ([MongoDB Docs](https://www.mongodb.com/docs/))
- BeautifulSoup for HTML parsing ([BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/))
- Related works: [Investing.com Economic Calendar](https://www.investing.com/economic-calendar/), [Forex Factory](https://www.forexfactory.com/calendar)
- Networking protocols: REST, CORS, concurrent futures for parallel scraping

### 2.4 Project Category
Product-based project with research elements in AI-driven signal generation and advanced scraping.

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

## Project Planning

- **Week 1-2:** Requirements, tech stack, initial backend and database setup.
- **Week 3-4:** Implement Selenium-based scrapers and data pipeline.
- **Week 5-6:** Develop REST APIs and networking layer (FastAPI, CORS).
- **Week 7-8:** Integrate AI signal generation and frontend dashboard.
- **Week 9:** Testing, optimization, documentation.
- **Week 10:** Final review, deployment, and presentation.

*(For group work: assign scraping, backend, frontend, and AI integration to different members.)*

## Project Feasibility

- **Technical Feasibility:**  
  Uses proven tools (Selenium, FastAPI, MongoDB, React). Risks include website structure changes and anti-bot measures, mitigated by Selenium Stealth and modular code.
- **Economic Feasibility:**  
  Open-source stack minimizes costs. Cloud/API usage may incur minor expenses.
- **Schedule Feasibility:**  
  10-week plan with parallel development and buffer for issues.

## Hardware and Software Requirements

- **Hardware:**  
  Standard PC/laptop, stable internet, optional cloud server.
- **Software:**  
  - Python 3.11+, Node.js, MongoDB
  - Selenium, webdriver-manager, selenium-stealth, requests, beautifulsoup4, fastapi, uvicorn, pymongo, dotenv
  - React, Vite, Tailwind CSS
  - AI API access (OpenRouter, Gemini)
  - Git, VS Code

## Diagrammatic Representation of the Overall System



*(Attach a system architecture diagram showing:)*  
- Data sources (websites/APIs)  
- Selenium-based scraper modules  
- Backend API (FastAPI)  
- Database (MongoDB)  
- AI signal generator  
- Frontend (React)  
- Networking flows (REST, concurrent scraping, CORS)

![logo](https://res.cloudinary.com/dkb1rdtmv/image/upload/v1745092521/mermaid-diagram-2025-04-20-005507_wa543w.png)