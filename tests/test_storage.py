import json
import pandas as pd
from scraper.storage import DataStorage

SAMPLE_PRODUCTS = [
    {
        "title": "گوشی سامسونگ A55",
        "price": 45000000,
        "discount": 5,
        "link": "https://example.com/1"
    },
    {
        "title": "گوشی سامسونگ S24",
        "price": 60000000,
        "discount": 0,
        "link": "https://example.com/2"
    }
]


def test_save_to_json(tmp_path):
    storage = DataStorage(output_dir=str(tmp_path))
    file_path = storage.save_to_json(SAMPLE_PRODUCTS, "test_products")

    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["price"] == 45000000


def test_save_to_csv(tmp_path):
    storage = DataStorage(output_dir=str(tmp_path))
    file_path = storage.save_to_csv(SAMPLE_PRODUCTS, "test_products")

    assert file_path.exists()
    df = pd.read_csv(file_path)
    assert len(df) == 2
    assert "title" in df.columns


def test_save_to_excel(tmp_path):
    storage = DataStorage(output_dir=str(tmp_path))
    result_path = storage.save_to_excel(SAMPLE_PRODUCTS, "test_products")

    df = pd.read_excel(result_path)
    assert len(df) == 2
