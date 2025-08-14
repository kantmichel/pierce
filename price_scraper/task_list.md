# Market Analysis Tool - Development Task List

## Phase 2: Sitemap Processing & URL Collection

### 2.0 XML Sitemap Parser ✅ COMPLETED
- [x] Create XML sitemap parser for product URL extraction
  - [x] Parse XML structure with xml.etree.ElementTree
  - [x] Extract URL, breadcrumb_eng, and breadcrumb_local fields
  - [x] Validate XML structure and handle malformed entities (&gtgt; fixes)
  - [x] Log parsing statistics and errors
- [x] Implement category-based URL filtering
  - [x] Load category keywords from config/categories.yaml
  - [x] Match breadcrumb paths against category keywords
  - [x] Apply configurable limits per category (exactly 10 URLs per category)
  - [x] Handle case-insensitive keyword matching
  - [x] Support multiple language breadcrumbs with HTML entity decoding
- [x] Generate filtered product URL lists
  - [x] Update config/products.csv with filtered URLs
  - [x] Add metadata columns (category, breadcrumb path)
  - [x] Validate URL accessibility before inclusion
  - [x] Generate summary statistics of extracted URLs
  - [x] Prevent duplicate URLs across multiple runs
- [x] XML file management
  - [x] Store XML sitemaps in data/xml/ directory
  - [x] Support for 24mx_sitemap.xml and xlmoto_sitemap.xml
  - [x] Add file validation and integrity checks
  - [x] Handle large XML files efficiently (18K+ entries)
  - [x] Handle namespace parsing correctly

**Results Achieved:**
- **120 total URLs extracted** (60 from each site)
- **24MX**: 14,919 entries processed → 60 URLs
- **XLMoto**: 18,188 entries processed → 60 URLs
- **6 categories**: helmets, chains, oils, tires, brake_pads, filters (10 URLs each)
- **Command**: `uv run python scripts/parse_sitemaps.py`

## Phase 3: Product Data Extraction

### 3.1 Base Crawler Implementation ✅ COMPLETED
- [x] Create abstract base crawler class with common functionality
  - [x] Define abstract methods for Firecrawl data processing
  - [x] Implement Firecrawl API integration and initialization
  - [x] Create base product data structure and result objects
  - [x] Add comprehensive logging integration for all operations
- [x] Implement rate limiting and request throttling
  - [x] Add configurable delay between requests
  - [x] Implement requests per second limiting with RateLimiter class
  - [x] Create semaphore-based concurrency control
  - [x] Add exponential backoff strategy for failed requests
  - [x] Built-in Firecrawl rate limiting respect
- [x] Add error handling and retry mechanisms
  - [x] Implement exponential backoff for retries (up to 3 attempts)
  - [x] Handle Firecrawl API errors and timeouts
  - [x] Add comprehensive error logging and categorization
  - [x] Create structured error reporting with CrawlResult
  - [x] Graceful fallback strategies for failed extractions
- [x] Create data validation and sanitization methods
  - [x] Validate extracted product names, URLs, and prices
  - [x] Sanitize and normalize text content
  - [x] Text cleaning with whitespace normalization
  - [x] Product data completeness validation
  - [x] Structured validation with clear error messages

**Results Achieved:**
- **BaseCrawler class** using Firecrawl API instead of direct HTTP scraping
- **Professional error handling** with retries and structured results
- **Async concurrent processing** with configurable limits
- **Rate limiting** respecting Firecrawl API constraints
- **Abstract interface** ready for site-specific implementations
- **Command**: Inherit from `BaseCrawler` and implement `_extract_product_data()`

### 3.2 EU Site Crawlers
- [ ] Build 24mx.co.uk product extractor using claude ai
  - [ ] Parse product details (name, brand, model, price)
  - [ ] Handle different product page layouts 
- [ ] Build xlmoto.co.uk product extractor using claude ai
  - [ ] Parse product details (name, brand, model, price)
  - [ ] Handle different product page layouts 

### 3.3 Turkish Site Crawlers
- [ ] Build motomax.com.tr search and extract system
  - [ ] Implement search functionality
  - [ ] Parse Turkish product pages
  - [ ] Handle TL currency parsing (18.900 TL format)
- [ ] Build mototas.com.tr search and extract system
  - [ ] Implement search functionality
  - [ ] Parse Turkish product pages
  - [ ] Handle TL currency parsing

## Phase 4: Data Processing & Normalization

### 4.1 Product Matching Engine
- [ ] Implement fuzzy string matching for product names
- [ ] Create brand/model matching algorithms
- [ ] Build confidence scoring system
- [ ] Handle language differences (EN/TR)

### 4.2 Data Normalization
- [ ] Standardize product names and descriptions
- [ ] Normalize pricing formats across sites
- [ ] Clean and validate extracted data
- [ ] Handle missing or incomplete data

## Phase 5: Currency Conversion

### 5.1 Exchange Rate Integration
- [ ] Integrate with exchange rate API
- [ ] Implement rate caching and refresh logic
- [ ] Handle EUR, GBP, TRY conversions
- [ ] Add historical rate tracking

### 5.2 Price Analysis
- [ ] Calculate price differences across markets
- [ ] Identify significant price gaps
- [ ] Account for currency fluctuations
- [ ] Generate pricing insights

## Phase 6: Database & Storage

### 6.1 Database Setup
- [ ] Initialize DuckDB database
- [ ] Create database connection manager
- [ ] Implement data repository layer
- [ ] Add database migration support

### 6.2 Data Persistence
- [ ] Store product information
- [ ] Track price history over time
- [ ] Maintain crawl session logs
- [ ] Cache exchange rates

## Phase 7: Market Analysis Engine

### 7.1 Comparison Logic
- [ ] Match products across markets
- [ ] Calculate market price differentials
- [ ] Identify arbitrage opportunities
- [ ] Analyze market positioning

### 7.2 Business Intelligence
- [ ] Generate market entry insights
- [ ] Calculate potential profit margins
- [ ] Assess competitive landscape
- [ ] Track market trends over time

## Phase 8: Reporting & Analytics

### 8.1 Report Generation
- [ ] Create market analysis reports
- [ ] Generate pricing comparison tables
- [ ] Build executive summary dashboards
- [ ] Export data in business formats (Excel, PDF)

### 8.2 Visualization
- [ ] Create pricing trend charts
- [ ] Build market opportunity visualizations
- [ ] Generate geographic price heat maps
- [ ] Add interactive data exploration

## Phase 9: Automation & Monitoring

### 9.1 Scheduling
- [ ] Implement automated crawling schedules
- [ ] Set up periodic market updates
- [ ] Create price change alerts
- [ ] Add monitoring dashboards

### 9.2 Quality Assurance
- [ ] Add data validation checks
- [ ] Implement crawling success monitoring
- [ ] Create error alerting system
- [ ] Add performance metrics tracking

## Phase 10: Business Integration

### 10.1 API Development
- [ ] Create REST API for data access
- [ ] Build authentication system
- [ ] Add rate limiting for API access
- [ ] Document API endpoints

### 10.2 Export Capabilities
- [ ] Generate business-ready reports
- [ ] Create data export pipelines
- [ ] Add custom report templates
- [ ] Implement scheduled reporting

## Immediate Next Steps (Current Priority)

1. **Set up development environment**
   - [ ] Install dependencies with `uv sync`
   - [ ] Configure API keys in `.env`
   - [ ] Add initial product URLs to `config/products.csv`

2. **Build foundation components**
   - [ ] Create database connection and schema
   - [ ] Implement base crawler class
   - [ ] Set up logging and configuration

3. **Develop first crawler**
   - [ ] Start with 24mx.co.uk product extraction
   - [ ] Test with a few sample product URLs
   - [ ] Validate data extraction accuracy

4. **Test end-to-end flow**
   - [ ] Extract products from EU sites
   - [ ] Search for matches on Turkish sites
   - [ ] Generate initial comparison report