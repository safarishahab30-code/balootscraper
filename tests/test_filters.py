import pytest

PRODUCTS_LIST = [
    {"title": "کالای الف", "price": 10000000, "discount": 10},
    {"title": "کالای ب", "price": 30000000, "discount": 0},
    {"title": "کالای ج", "price": 50000000, "discount": 25},
]


def filter_products(products, min_price=None, max_price=None):
    """تابع کمکی فیلتر قیمت (جهت اعتبارسنجی لاجیک CLI)"""
    res = products
    if min_price is not None:
        res = [p for p in res if p["price"] >= min_price]
    if max_price is not None:
        res = [p for p in res if p["price"] <= max_price]
    return res


def sort_products(products, sort_by="price_asc"):
    """تابع کمکی مرتب‌سازی داده‌ها"""
    if sort_by == "price_asc":
        return sorted(products, key=lambda x: x["price"])
    elif sort_by == "price_desc":
        return sorted(products, key=lambda x: x["price"], reverse=True)
    elif sort_by == "discount_desc":
        return sorted(products, key=lambda x: x.get("discount", 0), reverse=True)
    return products


def test_filter_min_price():
    """تست فیلتر حداقل قیمت"""
    filtered = filter_products(PRODUCTS_LIST, min_price=20000000)
    assert len(filtered) == 2
    assert all(p["price"] >= 20000000 for p in filtered)


def test_filter_max_price():
    """تست فیلتر حداکثر قیمت"""
    filtered = filter_products(PRODUCTS_LIST, max_price=40000000)
    assert len(filtered) == 2
    assert all(p["price"] <= 40000000 for p in filtered)


def test_sort_price_desc():
    """تست سورت نزولی قیمت"""
    sorted_list = sort_products(PRODUCTS_LIST, sort_by="price_desc")
    assert sorted_list[0]["price"] == 50000000
    assert sorted_list[-1]["price"] == 10000000


def test_sort_discount_desc():
    """تست سورت نزولی بیشترین تخفیف"""
    sorted_list = sort_products(PRODUCTS_LIST, sort_by="discount_desc")
    assert sorted_list[0]["discount"] == 25
