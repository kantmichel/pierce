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

### 2.1 Base Crawler Implementation
- [ ] Create abstract base crawler class with common functionality
  - [ ] Define abstract methods for URL processing
  - [ ] Implement common HTTP request handling
  - [ ] Add user agent rotation and headers management
  - [ ] Create base product data structure
  - [ ] Add logging integration for all crawler activities
- [ ] Implement rate limiting and request throttling
  - [ ] Add configurable delay between requests
  - [ ] Implement requests per second limiting
  - [ ] Create queue system for request management
  - [ ] Add backoff strategy for failed requests
  - [ ] Monitor and respect robots.txt files
- [ ] Add error handling and retry mechanisms
  - [ ] Implement exponential backoff for retries
  - [ ] Handle HTTP timeout and connection errors
  - [ ] Add specific handling for 429 (rate limit) responses
  - [ ] Log and categorize different error types
  - [ ] Create fallback strategies for failed extractions
- [ ] Create data validation and sanitization methods
  - [ ] Validate extracted product names and prices
  - [ ] Sanitize HTML and remove unwanted characters
  - [ ] Normalize price formats and currency symbols
  - [ ] Validate URLs and image links
  - [ ] Check for required fields completeness

### 2.2 EU Site Crawlers
- [ ] Build 24mx.co.uk product extractor
  - [ ] Parse product details (name, brand, model, price)
  - [ ] Handle different product page layouts
  - [ ] Extract availability and stock information
- [ ] Build xlmoto.co.uk product extractor
  - [ ] Parse product details (name, brand, model, price)
  - [ ] Handle different product page layouts
  - [ ] Extract availability and stock information

### 2.3 Turkish Site Crawlers
- [ ] Build motomax.com.tr search and extract system
  - [ ] Implement search functionality
  - [ ] Parse Turkish product pages
  - [ ] Handle TL currency parsing (18.900 TL format)
- [ ] Build mototas.com.tr search and extract system
  - [ ] Implement search functionality
  - [ ] Parse Turkish product pages
  - [ ] Handle TL currency parsing

## Phase 3: Data Processing & Normalization

### 3.1 Product Matching Engine
- [ ] Implement fuzzy string matching for product names
- [ ] Create brand/model matching algorithms
- [ ] Build confidence scoring system
- [ ] Handle language differences (EN/TR)

### 3.2 Data Normalization
- [ ] Standardize product names and descriptions
- [ ] Normalize pricing formats across sites
- [ ] Clean and validate extracted data
- [ ] Handle missing or incomplete data

## Phase 4: Currency Conversion

### 4.1 Exchange Rate Integration
- [ ] Integrate with exchange rate API
- [ ] Implement rate caching and refresh logic
- [ ] Handle EUR, GBP, TRY conversions
- [ ] Add historical rate tracking

### 4.2 Price Analysis
- [ ] Calculate price differences across markets
- [ ] Identify significant price gaps
- [ ] Account for currency fluctuations
- [ ] Generate pricing insights

## Phase 5: Database & Storage

### 5.1 Database Setup
- [ ] Initialize DuckDB database
- [ ] Create database connection manager
- [ ] Implement data repository layer
- [ ] Add database migration support

### 5.2 Data Persistence
- [ ] Store product information
- [ ] Track price history over time
- [ ] Maintain crawl session logs
- [ ] Cache exchange rates

## Phase 6: Market Analysis Engine

### 6.1 Comparison Logic
- [ ] Match products across markets
- [ ] Calculate market price differentials
- [ ] Identify arbitrage opportunities
- [ ] Analyze market positioning

### 6.2 Business Intelligence
- [ ] Generate market entry insights
- [ ] Calculate potential profit margins
- [ ] Assess competitive landscape
- [ ] Track market trends over time

## Phase 7: Reporting & Analytics

### 7.1 Report Generation
- [ ] Create market analysis reports
- [ ] Generate pricing comparison tables
- [ ] Build executive summary dashboards
- [ ] Export data in business formats (Excel, PDF)

### 7.2 Visualization
- [ ] Create pricing trend charts
- [ ] Build market opportunity visualizations
- [ ] Generate geographic price heat maps
- [ ] Add interactive data exploration

## Phase 8: Automation & Monitoring

### 8.1 Scheduling
- [ ] Implement automated crawling schedules
- [ ] Set up periodic market updates
- [ ] Create price change alerts
- [ ] Add monitoring dashboards

### 8.2 Quality Assurance
- [ ] Add data validation checks
- [ ] Implement crawling success monitoring
- [ ] Create error alerting system
- [ ] Add performance metrics tracking

## Phase 9: Business Integration

### 9.1 API Development
- [ ] Create REST API for data access
- [ ] Build authentication system
- [ ] Add rate limiting for API access
- [ ] Document API endpoints

### 9.2 Export Capabilities
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