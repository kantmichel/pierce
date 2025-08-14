import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv
import yaml
import html
from dataclasses import dataclass
from urllib.parse import urlparse

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SitemapEntry:
    """Represents a single entry from the sitemap XML."""
    url: str
    breadcrumb_eng: str
    breadcrumb_local: str
    category: Optional[str] = None


class SitemapParser:
    """Parses XML sitemaps and extracts product URLs by category."""
    
    def __init__(self, categories_config_path: str = "config/categories.yaml"):
        """Initialize the sitemap parser."""
        self.categories_config_path = Path(categories_config_path)
        self.categories = self._load_categories()
        
    def _load_categories(self) -> Dict:
        """Load category configuration from YAML file."""
        try:
            with open(self.categories_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('categories', {})
        except FileNotFoundError:
            logger.error(f"Categories config file not found: {self.categories_config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing categories YAML: {e}")
            return {}
    
    def parse_xml_file(self, xml_file_path: str) -> List[SitemapEntry]:
        """Parse XML sitemap file and extract all entries."""
        xml_path = Path(xml_file_path)
        
        if not xml_path.exists():
            logger.error(f"XML file not found: {xml_file_path}")
            return []
        
        try:
            # Read and clean the XML content to handle leading whitespace and malformed entities
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Fix common malformed entities
            content = content.replace('&gtgt;', '&gt;')  # Fix double gt entity
            content = content.replace('&ltlt;', '&lt;')  # Fix double lt entity if any
            
            # Parse the cleaned content
            root = ET.fromstring(content)
            
            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            entries = []
            urls = root.findall('.//ns:url', namespace)
            
            for url_elem in urls:
                loc_elem = url_elem.find('ns:loc', namespace)
                # Breadcrumb elements ARE namespaced (contrary to your example structure)
                breadcrumb_eng_elem = url_elem.find('ns:breadCrumb_eng', namespace)  
                breadcrumb_local_elem = url_elem.find('ns:breadCrumb_local', namespace)
                
                if loc_elem is not None:
                    entry = SitemapEntry(
                        url=loc_elem.text.strip(),
                        breadcrumb_eng=html.unescape(breadcrumb_eng_elem.text.strip()) if breadcrumb_eng_elem is not None else "",
                        breadcrumb_local=html.unescape(breadcrumb_local_elem.text.strip()) if breadcrumb_local_elem is not None else ""
                    )
                    entries.append(entry)
            
            logger.info(f"Parsed {len(entries)} entries from {xml_file_path}")
            return entries
            
        except ET.ParseError as e:
            logger.error(f"Error parsing XML file {xml_file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing {xml_file_path}: {e}")
            return []
    
    def categorize_entry(self, entry: SitemapEntry) -> Optional[str]:
        """Determine which category an entry belongs to based on breadcrumbs."""
        breadcrumb_text = f"{entry.breadcrumb_eng} {entry.breadcrumb_local}".lower()
        
        for category_name, category_config in self.categories.items():
            keywords = category_config.get('keywords', [])
            
            for keyword in keywords:
                if keyword.lower() in breadcrumb_text:
                    return category_name
        
        return None
    
    def filter_by_categories(self, entries: List[SitemapEntry]) -> Dict[str, List[SitemapEntry]]:
        """Filter entries by categories and apply limits."""
        categorized = {}
        
        
        for entry in entries:
            category = self.categorize_entry(entry)
            if category:
                entry.category = category
                if category not in categorized:
                    categorized[category] = []
                
                # Check if we haven't reached the limit for this category
                category_limit = self.categories[category].get('limit', 10)
                if len(categorized[category]) < category_limit:
                    categorized[category].append(entry)
        
        # Log statistics
        for category, category_entries in categorized.items():
            logger.info(f"Found {len(category_entries)} entries for category '{category}'")
        
        return categorized
    
    def validate_url_accessibility(self, url: str) -> bool:
        """Basic URL validation (structure check, not actual HTTP request)."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except Exception:
            return False
    
    def generate_csv_output(self, categorized_entries: Dict[str, List[SitemapEntry]], 
                           site_name: str, output_path: str = "config/products.csv") -> None:
        """Generate CSV file with filtered URLs."""
        output_file = Path(output_path)
        
        # Read existing CSV if it exists
        existing_entries = []
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_entries = list(reader)
            except Exception as e:
                logger.warning(f"Could not read existing CSV: {e}")
        
        # Add new entries
        new_entries = []
        for category, entries in categorized_entries.items():
            for entry in entries:
                if self.validate_url_accessibility(entry.url):
                    new_entries.append({
                        'site': site_name,
                        'product_url': entry.url,
                        'status': 'pending',
                        'category': category,
                        'breadcrumb': entry.breadcrumb_eng
                    })
        
        # Combine existing and new entries, removing duplicates by URL
        all_entries = existing_entries.copy()
        existing_urls = {entry.get('product_url') for entry in existing_entries}
        
        for new_entry in new_entries:
            if new_entry['product_url'] not in existing_urls:
                all_entries.append(new_entry)
        
        # Write updated CSV
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['site', 'product_url', 'status', 'category', 'breadcrumb']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_entries)
            
            logger.info(f"Generated CSV with {len(all_entries)} total entries at {output_path}")
            logger.info(f"Added {len(new_entries)} new entries for {site_name}")
            
        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
    
    def generate_statistics(self, categorized_entries: Dict[str, List[SitemapEntry]], 
                          site_name: str) -> Dict:
        """Generate summary statistics."""
        stats = {
            'site': site_name,
            'total_entries': sum(len(entries) for entries in categorized_entries.values()),
            'categories': {}
        }
        
        for category, entries in categorized_entries.items():
            stats['categories'][category] = {
                'count': len(entries),
                'limit': self.categories[category].get('limit', 10),
                'sample_urls': [entry.url for entry in entries[:3]]  # First 3 URLs as sample
            }
        
        return stats
    
    def process_sitemap(self, xml_file_path: str, site_name: str) -> Dict:
        """Main method to process a sitemap file."""
        logger.info(f"Processing sitemap for {site_name}: {xml_file_path}")
        
        # Parse XML file
        entries = self.parse_xml_file(xml_file_path)
        if not entries:
            logger.warning(f"No entries found in {xml_file_path}")
            return {}
        
        # Filter by categories
        categorized_entries = self.filter_by_categories(entries)
        
        # Generate CSV output
        self.generate_csv_output(categorized_entries, site_name)
        
        # Generate and return statistics
        stats = self.generate_statistics(categorized_entries, site_name)
        
        logger.info(f"Completed processing {site_name}: {stats['total_entries']} URLs extracted")
        return stats


def main():
    """Example usage of the SitemapParser."""
    parser = SitemapParser()
    
    # Process 24mx sitemap
    if Path("data/xml/24mx_sitemap.xml").exists():
        stats_24mx = parser.process_sitemap("data/xml/24mx_sitemap.xml", "24mx")
        print("24MX Statistics:", stats_24mx)
    
    # Process xlmoto sitemap
    if Path("data/xml/xlmoto_sitemap.xml").exists():
        stats_xlmoto = parser.process_sitemap("data/xml/xlmoto_sitemap.xml", "xlmoto")
        print("XLMoto Statistics:", stats_xlmoto)


if __name__ == "__main__":
    main()