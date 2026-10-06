# scraper/analyzer.py

def analyze_products(products: list[dict], brand: str | None = None) -> dict:
    if brand:
        filtered = [
            p for p in products 
            if brand.strip().lower() in p.get("title", "").lower()
        ]
    else:
        filtered = products

    prices = [
        p["price"] for p in filtered 
        if isinstance(p.get("price"), (int, float))
    ]

    total_count = len(filtered)
    priced_count = len(prices)
    unpriced_count = total_count - priced_count

    stats = {
        "total": total_count,
        "priced_count": priced_count,
        "unpriced_count": unpriced_count,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "avg_price": int(sum(prices) / priced_count) if priced_count else 0,
    }
    return stats
