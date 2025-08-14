# Motorcycle Parts Market Analysis Tool

This system provides competitive intelligence by comparing product pricing between established European markets (24mx.co.uk, xlmoto.co.uk) and emerging Turkish markets (motomax.com.tr, mototas.com.tr).

## Business Overview

This tool enables strategic market analysis considering expansion into new geographic markets by:

- Conducting systematic pricing audits across different markets
- Identifying market entry opportunities and competitive positioning
- Analyzing price elasticity and market dynamics across currencies
- Generating comprehensive market intelligence reports
- Tracking pricing trends and market movements over time

**Primary Use Cases:**
- Market entry feasibility analysis
- Competitive pricing strategy development
- Cross-border arbitrage opportunity identification
- Regional market dynamics assessment

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Firecrawl API key (for web scraping)
- Exchange rate API key (optional, for currency conversion)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd price_scraper
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Add product URLs**
   - Edit `config/products.csv`
   - Add URLs from 24mx.co.uk and xlmoto.co.uk

5. **Run the tool**
   ```bash
   uv run python -m src.main
   ```

## 📁 Project Structure

```
├── src/
│   ├── crawlers/          # Website scrapers
│   ├── processors/        # Data processing & normalization
│   ├── models/           # Data models
│   ├── storage/          # Database layer (DuckDB)
│   ├── comparison/       # Price comparison logic
│   ├── reports/          # Report generation
│   └── utils/            # Configuration & logging
├── config/
│   ├── products.csv      # Product URLs to scrape
│   ├── sites.yaml        # Website configurations
│   └── settings.yaml     # Application settings
├── data/                 # Database & cache files
├── output/               # Generated reports
└── logs/                 # Application logs
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here
LOG_LEVEL=INFO
DATABASE_PATH=data/moto_prices.duckdb
```

### Product URLs

Add product URLs to `config/products.csv`:

```csv
site,product_url,status
24mx,https://www.24mx.co.uk/motorcycle-helmets/agv-k6-helmet,pending
xlmoto,https://www.xlmoto.co.uk/motorcycle-tires/michelin-pilot-road-5,pending
```

### Site Configuration

Modify `config/sites.yaml` to adjust:
- CSS selectors for data extraction
- Rate limiting settings
- Search parameters for Turkish sites

## 🛠️ Usage

### Basic Price Comparison

```bash
# Run full comparison
uv run python -m src.main

# Run for specific site only
uv run python scripts/run_crawl.py --site 24mx

# Export results
uv run python scripts/export_data.py --format csv
```

### Command Line Options

```bash
uv run moto-compare --help
```

## 📊 Output Formats

The tool generates reports in multiple formats:

- **JSON**: Structured data for further processing
- **CSV**: Spreadsheet-friendly format
- **HTML**: Human-readable reports with charts

Reports are saved to the `output/` directory.

## 🔍 Features

### Product Matching
- Fuzzy string matching for product names
- Brand and model-based matching
- Configurable confidence thresholds

### Currency Conversion
- Real-time exchange rates
- Historical rate tracking
- Automatic EUR/GBP ↔ TRY conversion

### Price Tracking
- Historical price data storage
- Price change alerts
- Trend analysis

### Data Export
- Multiple export formats
- Scheduled reports
- API integration ready

## 📈 Supported Sites

### European Sites (Source)
- **24mx.co.uk** - Motorcycle parts and accessories
- **xlmoto.co.uk** - Motorcycle gear and parts

### Turkish Sites (Target)
- **motomax.com.tr** - Turkish motorcycle retailer
- **mototas.com.tr** - Turkish motorcycle parts supplier

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This tool is for educational and research purposes. Please ensure you comply with the terms of service of all websites being scraped. Be respectful with your requests and implement appropriate delays between requests.

## 🐛 Troubleshooting

### Common Issues

**API Key Issues**
- Ensure your Firecrawl API key is valid and has sufficient credits
- Check that environment variables are properly loaded

**Database Issues**
- Ensure the `data/` directory exists and is writable
- Check DuckDB version compatibility

**Scraping Issues**
- Websites may change their structure; update selectors in `config/sites.yaml`
- Respect rate limits to avoid being blocked

### Getting Help

- Check the logs in `logs/app.log`
- Review configuration files for syntax errors
- Ensure all dependencies are properly installed

## 🗺️ Roadmap

- [ ] Support for additional European sites
- [ ] Mobile app integration
- [ ] Real-time price alerts via email/SMS
- [ ] Advanced analytics and insights
- [ ] Integration with motorcycle forums and communities