# AI Development Task List: Credit Card Campaign Comparison App

This document serves as a step-by-step guide for an AI agent to build the application.

## 1. Project Initialization
- [ ] Initialize Next.js 14 project: `npx create-next-app@latest frontend --js --no-eslint --no-tailwind --no-src-dir --app --no-turbopack --import-alias "@/*"`
- [ ] Install Node.js dependencies: `cd frontend && npm install @supabase/supabase-js`
- [ ] Create Supabase project at [supabase.com](https://supabase.com)
- [ ] Create `.env.local` in frontend with Supabase credentials:
    ```
    NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
    NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
    ```
- [ ] Create project structure:
    - `frontend/` (Next.js app)
    - `scraper/` (Python scripts)

## 2. Database Setup
- [ ] Create `lib/supabase.js` in frontend:
    ```javascript
    import { createClient } from '@supabase/supabase-js'
    export const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    )
    ```
- [ ] Create schema in Supabase Dashboard → SQL Editor:
    - `banks` (id, name, slug, color, logo_url, website_url, created_at)
    - `cards` (id, bank_id, name, slug, type, created_at)
    - `campaigns` (id, card_id, title, description, merchant_name, merchant_pattern, discount_type, discount_rate, max_discount, min_spend, start_date, end_date, conditions, source_url, scraped_at, is_active)
    - Foreign keys: `cards.bank_id` → `banks.id`, `campaigns.card_id` → `cards.id`
- [ ] Configure Row Level Security (RLS) policies:
    - Enable RLS on all tables
    - Allow public read access (SELECT) for all tables
    - Allow authenticated write access (INSERT/UPDATE) for scraper (service role key)
- [ ] Seed initial data for 5 banks and their cards via SQL Editor or Supabase Studio.
- [ ] Seed sample campaign data (realistic test data for each card) so the app works before scrapers are ready.

## 3. Comparison Engine + API (Next.js)
- [ ] Implement `lib/engine.js`: Fuzzy matching (lowercase includes for MVP) + savings calculation logic.
- [ ] Create `GET /api/banks`:
    - Use Supabase: `supabase.from('banks').select('*, cards(*)')`
    - Return list of banks with their cards included (single endpoint, no separate `/api/cards`).
- [ ] Create `POST /api/compare`:
    - Input: `{ selectedCards: [], merchant: "Trendyol", amount: 500 }`
    - Query: `supabase.from('campaigns').select('*, cards(*, banks(*))').in('card_id', selectedCards).eq('is_active', true)`
    - Logic: Find matching campaigns using fuzzy search on `merchant_pattern`.
    - Logic: Calculate potential savings using `discount_type` (percentage vs fixed TL).
    - Output: Sorted list of cards with savings and campaign details.
- [ ] Write unit tests for comparison engine and fuzzy matching.

## 4. Frontend UI Implementation
- [ ] **Step 1: Bank & Card Selection**
    - Component: `BankSelector` (Grid of bank logos with bank-specific colors).
    - Component: `CardSelector` (Multi-select chips).
    - State: Track selected bank IDs and card IDs.
- [ ] **Step 2: Spending Input**
    - Component: `SpendingForm`.
    - Input: Merchant name (Text with simple suggestions from existing campaign merchants).
    - Input: Amount (Number in TL).
- [ ] **Step 3: Results Display**
    - Component: `ResultsPanel`.
    - Display cards sorted by highest saving.
    - Component: `CampaignCard` to show details (savings, conditions, source link).
- [ ] Apply styling (CSS) for a modern, responsive look (Glassmorphism, bank-specific color palettes).

## 5. Scraper Implementation (Python)
- [ ] Set up Python environment: `pip install beautifulsoup4 requests playwright supabase python-dotenv && playwright install`
- [ ] Create `.env` in scraper directory with Supabase Service Role Key:
    ```
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
    ```
- [ ] Create `scraper/main.py` as the entry point.
- [ ] Implement `scraper/supabase_client.py`:
    ```python
    from supabase import create_client, Client
    import os
    from dotenv import load_dotenv

    load_dotenv()
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    ```
- [ ] Implement `scraper/banks/akbank.py`: Scrape Axess/Wings campaigns.
- [ ] Implement `scraper/banks/garanti.py`: Scrape Bonus/Shop&Fly campaigns.
- [ ] Implement `scraper/banks/yapikredi.py`: Scrape World/Play campaigns.
- [ ] Implement `scraper/banks/isbank.py`: Scrape Maximum campaigns.
- [ ] Implement `scraper/banks/finansbank.py`: Scrape CardFinans campaigns.
- [ ] Each scraper uses: `supabase.table('campaigns').upsert(data).execute()`
- [ ] Add error handling, rate limiting, and logging to each scraper.
- [ ] Test scrapers individually and ensure data is populated in Supabase.

## 6. Verification
- [ ] Run scraper to populate Supabase with real data.
- [ ] Verify data in Supabase Dashboard → Table Editor.
- [ ] Test the full user flow on localhost with real scraped data.
- [ ] Check if "Trendyol" input matches "Trendyol.com" campaigns (Fuzzy match verification).
- [ ] Test responsive design on different screen sizes.
- [ ] Deploy to Vercel and verify Supabase connection with production env variables.
