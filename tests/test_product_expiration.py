"""Tests for Product Expiration Tracker."""
import pytest
from datetime import date, datetime
from custom_components.product_expiration.storage import ProductStorage
from custom_components.product_expiration.coordinator import ProductExpirationCoordinator
from unittest.mock import Mock, AsyncMock, patch
import json


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = Mock()
    hass.data = {}
    return hass


@pytest.fixture
async def storage(mock_hass):
    """Create storage instance."""
    store = ProductStorage(mock_hass)
    store._store = AsyncMock()
    store._store.async_load = AsyncMock(return_value=None)
    store._store.async_save = AsyncMock()
    await store.async_load()
    return store


@pytest.mark.asyncio
async def test_add_product_generates_unique_id(storage):
    """Test that adding products generates unique IDs."""
    product1 = {"name": "Mayonesa", "expiry": "2027-02-14"}
    product2 = {"name": "Mayonesa", "expiry": "2027-02-14"}  # Same data
    
    id1 = await storage.async_add_product(product1.copy())
    id2 = await storage.async_add_product(product2.copy())
    
    assert id1 != id2, "IDs should be unique even for identical products"
    assert len(storage.get_products()) == 2


@pytest.mark.asyncio
async def test_add_product_preserves_existing_id(storage):
    """Test that existing IDs are preserved."""
    product = {"id": "custom-id-123", "name": "Test", "expiry": "2027-01-01"}
    
    returned_id = await storage.async_add_product(product)
    
    assert returned_id == "custom-id-123"
    saved = storage.get_products()[0]
    assert saved["id"] == "custom-id-123"


@pytest.mark.asyncio
async def test_remove_product(storage):
    """Test removing a product."""
    product = {"name": "Test", "expiry": "2027-01-01"}
    product_id = await storage.async_add_product(product)
    
    removed = await storage.async_remove_product(product_id)
    assert removed is True
    assert len(storage.get_products()) == 0
    
    # Try removing again
    removed = await storage.async_remove_product(product_id)
    assert removed is False


@pytest.mark.asyncio
async def test_update_product(storage):
    """Test updating a product."""
    product = {"name": "Original", "expiry": "2027-01-01", "quantity": 1}
    product_id = await storage.async_add_product(product)
    
    updated = await storage.async_update_product(product_id, {
        "name": "Updated",
        "quantity": 5
    })
    
    assert updated is True
    saved = storage.get_products()[0]
    assert saved["name"] == "Updated"
    assert saved["quantity"] == 5
    assert saved["expiry"] == "2027-01-01"  # Unchanged


@pytest.mark.asyncio
async def test_coordinator_handles_invalid_date(mock_hass):
    """Test that coordinator handles invalid dates gracefully."""
    storage = Mock()
    storage.get_products = Mock(return_value=[
        {"id": "1", "name": "Valid", "expiry": "2027-01-15"},
        {"id": "2", "name": "Invalid", "expiry": "not-a-date"},
        {"id": "3", "name": "Missing"},  # No expiry
    ])
    
    entry = Mock()
    entry.data = {}
    entry.options = {}
    
    with patch('custom_components.product_expiration.coordinator.dt_util') as mock_dt:
        mock_dt.now.return_value.date.return_value = date(2026, 8, 26)
        
        coordinator = ProductExpirationCoordinator(mock_hass, storage, entry)
        
        # Should not raise
        data = await coordinator._async_update_data()
        
        # Only valid product should be processed
        assert data["total_count"] == 1
        assert data["products"][0]["name"] == "Valid"


@pytest.mark.asyncio
async def test_coordinator_uses_warn_days_from_config(mock_hass):
    """Test that coordinator uses configured warn_days."""
    storage = Mock()
    storage.get_products = Mock(return_value=[
        {"id": "1", "name": "Product", "expiry": "2026-08-28"},  # 2 days
    ])
    
    entry = Mock()
    entry.data = {"warn_days": [30, 15, 3, 1]}
    entry.options = {}
    
    with patch('custom_components.product_expiration.coordinator.dt_util') as mock_dt:
        mock_dt.now.return_value.date.return_value = date(2026, 8, 26)
        
        coordinator = ProductExpirationCoordinator(mock_hass, storage, entry)
        data = await coordinator._async_update_data()
        
        # 2 days is greater than min(warn_days)=1, so should be "expiring soon"
        assert data["expiring_soon_count"] == 1
        assert data["warn_days"] == [30, 15, 3, 1]


@pytest.mark.asyncio
async def test_coordinator_builds_image_urls(mock_hass):
    """Test that coordinator builds image URLs correctly."""
    storage = Mock()
    storage.get_products = Mock(return_value=[
        {"id": "1", "name": "With image", "expiry": "2027-01-15", "image": "product.jpg"},
        {"id": "2", "name": "No image", "expiry": "2027-01-15"},
    ])
    
    entry = Mock()
    entry.data = {"photo_base_url": "http://192.168.1.100:8765"}
    entry.options = {}
    
    with patch('custom_components.product_expiration.coordinator.dt_util') as mock_dt:
        mock_dt.now.return_value.date.return_value = date(2026, 8, 26)
        
        coordinator = ProductExpirationCoordinator(mock_hass, storage, entry)
        data = await coordinator._async_update_data()
        
        products = data["products"]
        assert products[0]["image_url"] == "http://192.168.1.100:8765/product.jpg"
        assert products[1]["image_url"] is None


def test_date_normalization():
    """Test _normalize_date function."""
    from custom_components.product_expiration import _normalize_date
    
    # datetime object
    dt = datetime(2027, 2, 14, 15, 30)
    assert _normalize_date(dt) == "2027-02-14"
    
    # date object
    d = date(2027, 2, 14)
    assert _normalize_date(d) == "2027-02-14"
    
    # string
    s = "2027-02-14"
    assert _normalize_date(s) == "2027-02-14"
    
    # Invalid type
    with pytest.raises(ValueError):
        _normalize_date(12345)


@pytest.mark.asyncio
async def test_import_products(storage):
    """Test bulk import functionality."""
    products = [
        {"name": "Product 1", "expiry": "2027-01-15"},
        {"name": "Product 2", "expiry": "2027-02-20"},
        {"name": "Product 3", "expiry": "2027-03-10"},
    ]
    
    imported = await storage.async_import_products(products)
    
    assert imported == 3
    assert len(storage.get_products()) == 3
