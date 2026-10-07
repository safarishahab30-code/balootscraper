import pytest
from scraper.factory import get_parser
from scraper.parser import ProductParser
from scraper.zoomit_parser import ZoomitParser

def test_get_parser_technolife():
    parser = get_parser("https://www.technolife.ir/product-123")
    assert isinstance(parser, ProductParser)

def test_get_parser_zoomit():
    parser = get_parser("https://www.zoomit.ir/product-456")
    assert isinstance(parser, ZoomitParser)

def test_get_parser_invalid_domain():
    with pytest.raises(ValueError):
        get_parser("https://www.digikala.com/product-789")
