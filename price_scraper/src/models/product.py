from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ProductStatus(Enum):
    """Product availability status."""
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"
    UNKNOWN = "unknown"


class Currency(Enum):
    """Supported currencies."""
    EUR = "EUR"
    GBP = "GBP"
    TRY = "TRY"  # Turkish Lira (ISO code, displayed as TL on sites)
    USD = "USD"


@dataclass
class Product:
    """Product data model."""
    
    # Identifiers
    id: Optional[str] = None
    sku: Optional[str] = None
    
    # Basic info
    name: str = ""
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    
    # Pricing
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None  # Before discount
    currency: Currency = Currency.EUR
    
    # Availability
    status: ProductStatus = ProductStatus.UNKNOWN
    stock_quantity: Optional[int] = None
    
    # Source info
    site_name: str = ""
    url: str = ""
    image_urls: List[str] = field(default_factory=list)
    
    # Metadata
    extracted_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Matching info
    search_terms: List[str] = field(default_factory=list)
    normalized_name: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.currency, str):
            self.currency = Currency(self.currency)
        if isinstance(self.status, str):
            self.status = ProductStatus(self.status)
        if isinstance(self.price, (int, float)):
            self.price = Decimal(str(self.price))
        if isinstance(self.original_price, (int, float)):
            self.original_price = Decimal(str(self.original_price))
    
    @property
    def has_discount(self) -> bool:
        """Check if product has a discount."""
        if not self.price or not self.original_price:
            return False
        return self.original_price > self.price
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage."""
        if not self.has_discount:
            return None
        return float((self.original_price - self.price) / self.original_price * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "brand": self.brand,
            "model": self.model,
            "category": self.category,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "original_price": float(self.original_price) if self.original_price else None,
            "currency": self.currency.value,
            "status": self.status.value,
            "stock_quantity": self.stock_quantity,
            "site_name": self.site_name,
            "url": self.url,
            "image_urls": self.image_urls,
            "extracted_at": self.extracted_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "search_terms": self.search_terms,
            "normalized_name": self.normalized_name,
            "has_discount": self.has_discount,
            "discount_percentage": self.discount_percentage,
        }