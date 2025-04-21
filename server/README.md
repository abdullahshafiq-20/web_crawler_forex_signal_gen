# Web Crawler & Economic Event Signal Generator

## Motivation
*In the rapidly evolving financial sector, access to real-time, accurate economic event data is essential for informed trading decisions. This project is motivated by the need to automate the extraction, aggregation, and analysis of global economic events using advanced web scraping and networking techniques, ensuring timely delivery of actionable insights to traders and analysts.*

## Overview

The core idea behind this project is to create an automated, scalable platform for extracting, aggregating, and analyzing global economic event data from multiple online sources, with a focus on delivering actionable insights for financial trading—especially in the crypto market. The system leverages advanced web scraping, robust networking, and AI-driven analysis to provide real-time, high-quality data and trading signals to traders and analysts.

### 2.1 Significance of the Project

Access to timely and accurate economic event data is crucial for making informed trading decisions, particularly in the fast-moving crypto market. However, such data is often scattered across various sources, inconsistently formatted, and difficult to aggregate manually. This project addresses these challenges by automating the collection and synchronization of economic event data, ensuring reliability and up-to-date information. The work is significant due to its:
- Practicality: Automates a time-consuming and error-prone process for traders and analysts.
- Usefulness: Provides a unified, clean, and accessible dataset for financial analysis and trading strategies.
- Academic Value: Demonstrates the application of advanced scraping, data engineering, and AI in a real-world financial context.
- Impact: If successful, the platform can improve trading outcomes, reduce manual effort, and serve as a foundation for further research in financial data analysis and AI-driven trading.

### 2.2 Description of the Project

This project aims to solve the problem of fragmented and inconsistent economic event data by building a distributed web scraping and data analysis platform. The backend, built with Python and FastAPI, uses Selenium and BeautifulSoup to scrape economic calendars from sources like CashbackForex and ForexFactory, handling dynamic content and anti-bot measures. The scraped data is cleaned, deduplicated, normalized, and stored in MongoDB. REST APIs provide access to this data for both internal analysis and external clients. The frontend, built with React, visualizes the data and trading signals for end users. The system is designed to be modular, scalable, and secure, with features such as concurrent scraping, asynchronous APIs, and environment-based API key management. The scope of the work is generalized for financial markets but is particularly tailored for the crypto market, where real-time data and rapid response are critical.

### 2.3 Background of the Project

The project builds on a range of established tools and techniques:
- Selenium for dynamic web scraping ([Selenium Docs](https://www.selenium.dev/documentation/))
- Selenium Stealth and WebDriver Manager for anti-bot evasion and driver management
- FastAPI for high-performance backend APIs ([FastAPI Docs](https://fastapi.tiangolo.com/))
- MongoDB for flexible, scalable data storage ([MongoDB Docs](https://www.mongodb.com/docs/))
- BeautifulSoup for HTML parsing ([BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/))
- Related works: [Investing.com Economic Calendar](https://www.investing.com/economic-calendar/), [Forex Factory](https://www.forexfactory.com/calendar)
- Networking protocols: REST, CORS, concurrent futures for parallel scraping
- AI APIs: OpenRouter and Gemini for automated trading signal analysis

These resources provide the technical foundation for the project, while the integration of AI for signal generation represents a novel contribution.

### 2.4 Project Category

This project is a **Product-based** solution with research elements, specifically targeting the crypto market. It is designed to be a deployable platform that can be used by traders, analysts, and financial institutions to gain a competitive edge through automated data aggregation and AI-driven trading signals.

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

## API Endpoints

- **GET /**  
  Returns a welcome message to confirm the API is running.

- **GET /events**  
  Retrieves economic events from the database. Supports optional filters: start_date, end_date, countries, impact, and sources.

- **GET /scrape/cashbackforex**  
  Scrapes economic events from CashbackForex, saves them to the database, and returns the data.

- **GET /scrape/forexfactory**  
  Scrapes economic events from ForexFactory, saves today's data to the database, and returns the data.

- **GET /generate-signals**  
  Generates trading signals using AI based on today's economic events and saves them to the database.

- **GET /signals**  
  Retrieves generated trading signals. Optionally filter by date.

- **GET /scrape/all**  
  Runs both CashbackForex and ForexFactory scrapers in parallel, saves today's events from both sources, and returns a summary.