# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Turkish credit card campaign comparison web application** that helps users with multiple credit cards determine which card offers the best benefits/discounts for a specific purchase. Users input a merchant name and spending amount, and the app ranks their cards by potential savings from active campaigns.

**Current Status:** Planning phase - no source code implemented yet. See [implementation_plan.md](implementation_plan.md) for complete technical specification and [ai_todo_list.md](ai_todo_list.md) for implementation checklist.

**Supported Banks (5):** Akbank, Garanti BBVA, Yapı Kredi, İş Bankası, QNB Finansbank
**Total Cards:** ~10 cards across all banks (1-2 per bank)

## Development Commands (Planned)

Once implementation begins, these commands will be available:

### Frontend (Next.js)
```bash
npm run dev          # Start Next.js development server (http://localhost:3000)
npm run build        # Build for production
npm test             # Run Jest unit and integration tests
npm run test:api     # Run API endpoint integration tests
```

### Scraping (Python)
```bash
python scraper/main.py              # Run campaign scraper manually
pytest scraper/tests/               # Run scraper tests with mock data
```

### Database
```bash
sqlite3 data/campaigns.db           # Open database CLI
sqlite3 data/campaigns.db < scraper/schema.sql  # Initialize schema
```

## Architecture

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 14 (App Router) | SSR, API routes, single project structure |
| **Styling** | Vanilla CSS | Full control, framework-independent |
| **Database** | SQLite (better-sqlite3) | Lightweight MVP, no setup required |
| **Scraping** | Python + BeautifulSoup/Playwright | Strong scraping ecosystem |
| **Scheduler** | Cron (system-level) | Simple, reliable |
| **Deployment** | Vercel (frontend) + VPS (scraper) | Free tier available |

### Database Schema

Three tables with the following relationships:

```
BANKS (5 banks)
  ├── id, name, slug, logo_url, website_url
  └── Has many → CARDS

CARDS (~10 cards)
  ├── id, bank_id, name, slug, type
  └── Has many → CAMPAIGNS

CAMPAIGNS (active promotions)
  ├── id, card_id, title, description
  ├── merchant_name, merchant_pattern (for fuzzy matching)
  ├── discount_rate, max_discount, min_spend
  ├── start_date, end_date, is_active
  └── conditions, source_url, scraped_at
```

**Key Fields:**
- `merchant_pattern`: Used for fuzzy matching user input (e.g., "trendyol" matches "Trendyol.com")
- `discount_rate`: Percentage or fixed TL amount
- `max_discount`: Cap on total discount
- `min_spend`: Minimum purchase amount required

### Comparison Engine Logic

```
Input: { selectedCards: [1,2,3], merchant: "Trendyol", amount: 500 }

1. Get active campaigns for selected cards
2. For each campaign:
   a. Fuzzy match merchant_pattern with user input
   b. Check min_spend requirement
   c. Calculate savings: min(amount × discount_rate, max_discount)
   d. Validate conditions
3. Sort results by savings (highest first)
4. Return ranked card recommendations
```

## Project Structure (Planned)

```
/Users/melisyilmaz/berk/1/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── page.js             # Main page (3-step wizard UI)
│   │   ├── layout.js           # Root layout
│   │   ├── globals.css         # Design system (glassmorphism, gradients)
│   │   └── api/
│   │       ├── banks/route.js      # GET banks list
│   │       ├── cards/route.js      # GET cards by bank
│   │       └── compare/route.js    # POST comparison logic
│   ├── components/
│   │   ├── BankSelector.js     # Bank selection grid
│   │   ├── CardSelector.js     # Multi-select card chips
│   │   ├── SpendingForm.js     # Merchant + amount input
│   │   ├── ResultsPanel.js     # Sorted results display
│   │   └── CampaignCard.js     # Campaign detail card
│   └── lib/
│       ├── db.js               # SQLite connection (better-sqlite3)
│       └── engine.js           # Comparison engine + fuzzy matching
├── scraper/                     # Python scraping service
│   ├── main.py                 # Entry point (orchestrates all scrapers)
│   ├── banks/
│   │   ├── akbank.py           # Axess, Wings campaigns
│   │   ├── garanti.py          # Bonus, Shop&Fly campaigns
│   │   ├── yapikredi.py        # World, Play campaigns
│   │   ├── isbank.py           # Maximum campaigns
│   │   └── finansbank.py       # CardFinans campaigns
│   └── db.py                   # DB write operations
├── data/
│   └── campaigns.db            # SQLite database file
├── implementation_plan.md      # Full technical roadmap (377 lines)
├── ai_todo_list.md            # Implementation checklist
└── README.md
```

## Key Development Notes

### MVP-First Approach
- Implement core functionality before enhancements
- No user authentication in MVP
- Single-page application with 3-step wizard flow
- Focus on 5 banks, ~10 cards initially (easily expandable)

### Scraping Considerations
- **Target URLs**: Each bank has dedicated campaign pages (e.g., akbank.com/kampanyalar/kredi-karti)
- **Challenges**: Sites may change structure, apply rate limiting, or have mobile-only campaigns
- **Error Handling**: Each scraper needs alert mechanism for failures
- **Rate Limiting**: Add delays between requests
- **Fallback**: Manual JSON/CSV import script for critical failures
- **Scope**: Only public campaign pages (avoid ToS violations)

### UI/UX Flow
1. **Step 1**: Select banks → select cards (multi-select, displayed as chips)
2. **Step 2**: Enter merchant name (with autocomplete) + spending amount
3. **Step 3**: View results sorted by savings + campaign details

### Design Principles
- Mobile-first responsive design
- Glassmorphism style with modern gradients
- Bank-specific color palettes (Akbank: orange, Garanti: green, etc.)
- Minimal API calls (client-side filtering)

### Language
All documentation and UI copy is in **Turkish**.

## Getting Started

Since this project is in the planning phase:

1. **Review the full specification**: Read [implementation_plan.md](implementation_plan.md) for complete technical details including:
   - Database ER diagrams
   - Scraping architecture flowcharts
   - 5-phase development timeline (Gantt chart)
   - Deployment strategy

2. **Follow implementation sequence**: Use [ai_todo_list.md](ai_todo_list.md) as a checklist:
   - Phase 1: Next.js project initialization + database schema
   - Phase 2: Python scrapers for 5 banks
   - Phase 3: Comparison engine + API routes
   - Phase 4: Frontend UI components
   - Phase 5: Testing + deployment

3. **Initialize project** (when ready):
   ```bash
   npx create-next-app@latest frontend --js --no-eslint --no-tailwind --no-src-dir --app
   cd frontend && npm install better-sqlite3
   ```

4. **Create database schema**: Start with `scraper/schema.sql` and seed 5 banks + their cards

## Development Timeline

**Estimated Total:** ~15 days (2-3 weeks)
- Faz 1 (Infrastructure): 1-2 days
- Faz 2 (Scraping): 3-4 days
- Faz 3 (Comparison Engine): 2-3 days
- Faz 4 (Frontend UI): 3-4 days
- Faz 5 (Testing + Deploy): 2-3 days

## Testing Strategy

- **Unit Tests**: Comparison engine, fuzzy matching logic
- **Integration Tests**: API endpoints (`/api/banks`, `/api/cards`, `/api/compare`)
- **Scraper Tests**: Mock data validation for each bank scraper
- **Browser Tests**: Full user flow (select → input → results)
