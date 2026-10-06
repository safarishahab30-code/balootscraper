import json
import re
from bs4 import BeautifulSoup


class ZoomitParser:
    def _format_price(self, raw_price) -> str:
        if raw_price is None or raw_price == "":
            return "ناموجود"
        try:
            # حذف کاما یا کاراکترهای اضافه و تبدیل به عدد
            clean_num = int(str(raw_price).replace(",", "").replace("٬", "").strip())
            return f"{clean_num:,} تومان" if clean_num > 0 else "ناموجود"
        except (ValueError, TypeError):
            return "ناموجود"

    def parse_products(self, html_content: str):
        products = []
        soup = BeautifulSoup(html_content, "html.parser")

        # ۱. استخراج داده‌های ساختاریافته از __NEXT_DATA__
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag and script_tag.string:
            try:
                raw_json = json.loads(script_tag.string)
                page_props = raw_json.get("props", {}).get("pageProps", {})

                # جستجوی لیست محصولات در ساختارهای مختلف کش Next.js زومیت
                raw_items = []
                queries = page_props.get("dehydratedState", {}).get("queries", [])
                for q in queries:
                    state_data = q.get("state", {}).get("data", {})
                    if isinstance(state_data, dict):
                        if "results" in state_data and isinstance(state_data["results"], list):
                            raw_items = state_data["results"]
                            break
                        if "items" in state_data and isinstance(state_data["items"], list):
                            raw_items = state_data["items"]
                            break

                if not raw_items:
                    raw_items = (
                        page_props.get("productsData", {}).get("items")
                        or page_props.get("products", [])
                        or []
                    )

                for item in raw_items:
                    if not isinstance(item, dict):
                        continue

                    # استخراج نام محصول
                    title = (
                        item.get("name")
                        or item.get("title")
                        or item.get("faName")
                        or item.get("englishTitle")
                    )
                    if not title:
                        continue

                    # استخراج مقدار عددی قیمت از فیلدهای محتمل
                    price_val = (
                        item.get("minPrice")
                        or item.get("cheapestPrice")
                        or item.get("price")
                        or (
                            item.get("pricing", {}).get("minPrice")
                            if isinstance(item.get("pricing"), dict)
                            else None
                        )
                        or (
                            item.get("priceVariants", [{}])[0].get("price")
                            if item.get("priceVariants")
                            else None
                        )
                    )

                    slug = item.get("slug") or item.get("id") or ""
                    link = f"https://www.zoomit.ir/product/{slug}/" if slug else ""

                    products.append({
                        "title": str(title).strip(),
                        "price": self._format_price(price_val),
                        "link": link
                    })

                if products:
                    return products
            except Exception:
                pass

        # ۲. فال‌بک HTML: در صورتی که ساختار JSON در دسترس نباشد
        product_links = soup.find_all(
            "a",
            href=re.compile(r"^/product/(?!list|compare|category|brand).*")
        )
        seen_links = set()

        for link_elem in product_links:
            href = link_elem.get("href", "")
            if not href or href in seen_links:
                continue

            h_tag = link_elem.find(["h2", "h3", "h4", "p"])
            title = h_tag.get_text(strip=True) if h_tag else link_elem.get_text(strip=True)

            if len(title) < 5 or title in ["مشاهده همه", "مقایسه", "خانه", "محصولات"]:
                continue

            seen_links.add(href)
            full_link = f"https://www.zoomit.ir{href}" if href.startswith("/") else href

            container = link_elem.find_parent("div") or link_elem
            price_match = re.search(r'([\d,٬]+)\s*(تومان|ریال)', container.get_text())
            price_text = "ناموجود"

            if price_match:
                price_text = self._format_price(price_match.group(1))

            products.append({
                "title": title.strip(),
                "price": price_text,
                "link": full_link
            })

        return products
