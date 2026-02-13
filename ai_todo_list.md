# AI Development Task List: Credit Card Campaign Comparison App

This document serves as a step-by-step guide for an AI agent to build the application.

## 1. Project Initialization
- [ ] Initialize Next.js 14 project: `npx create-next-app@latest frontend --js --no-eslint --no-tailwind --no-src-dir --app --no-turbopack --import-alias "@/*"`
- [ ] Install dependencies: `npm install better-sqlite3 playwright beautifulsoup4 requests` (Backend/Scraper dependencies)
- [ ] Create project structure:
    - `frontend/` (Next.js app)
    - `scraper/` (Python scripts)
    - `data/` (SQLite database)

## 2. Database Setup
- [ ] Create `lib/db.js` in frontend for database connection.
- [ ] Create schema script `scraper/schema.sql` with tables:
    - `banks` (id, name, slug, color, logo)
    - `cards` (id, bank_id, name, slug)
    - `campaigns` (id, card_id, title, description, merchant, discount_rate, conditions, start_date, end_date)
- [ ] Run schema creation script to initialize `data/campaigns.db`.
- [ ] Seed initial data for 5 banks and their cards.

## 3. Scraper Implementation (Python)
- [ ] Create `scraper/main.py` as the entry point.
- [ ] Implement `scraper/banks/akbank.py`: Scrape Axess/Wings campaigns.
- [ ] Implement `scraper/banks/garanti.py`: Scrape Bonus/Shop&Fly campaigns.
- [ ] Implement `scraper/banks/yapikredi.py`: Scrape World/Play campaigns.
- [ ] Implement `scraper/banks/isbank.py`: Scrape Maximum campaigns.
- [ ] Implement `scraper/banks/finansbank.py`: Scrape CardFinans campaigns.
- [ ] Implement `scraper/db.py` to save scraped data to SQLite.
- [ ] Test scrapers individually and ensure data is populated.

## 4. Backend API (Next.js)
- [ ] Create `GET /api/banks`: Return list of banks.
- [ ] Create `GET /api/cards?bankId=...`: Return cards for a bank.
- [ ] Create `POST /api/compare`:
    - Input: `{ selectedCards: [], merchant: "Trendyol", amount: 500 }`
    - Logic: Find matching campaigns using fuzzy search on `merchant`.
    - Logic: Calculate potential savings for each card using rules.
    - Output: Sorted list of cards with savings and campaign details.

## 5. Frontend UI Implementation
- [ ] **Step 1: Bank & Card Selection**
    - Component: `BankSelector` (Grid of bank logos).
    - Component: `CardSelector` (Multi-select chips).
    - State: Track selected bank IDs and card IDs.
- [ ] **Step 2: Spending Input**
    - Component: `SpendingForm`.
    - Input: Merchant name (Text with simple suggestions).
    - Input: Amount (Number).
- [ ] **Step 3: Results Display**
    - Component: `ResultsPanel`.
    - Display cards sorted by highest saving.
    - Component: `CampaignCard` to show details.
- [ ] Apply styling (CSS) for a modern, responsive look (Glassmorphism).

## 6. Verification
- [ ] Run scraper to populate DB with real data.
- [ ] Test the full user flow on localhost.
- [ ] Check if "Trendyol" input matches "Trendyol.com" campaigns (Fuzzy match verification).
