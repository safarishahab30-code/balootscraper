import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class ZoomitParser:
    """استخراج محصولات و قیمت‌ها از صفحات زومیت."""

    BASE_URL = "https://www.zoomit.ir"

    @staticmethod
    def _normalize_digits(value: Any) -> str:
        """تبدیل ارقام فارسی و عربی به انگلیسی."""
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        english_digits = "0123456789"

        translation_table = str.maketrans(
            persian_digits + arabic_digits,
            english_digits + english_digits,
        )

        return str(value).translate(translation_table)

    def _format_price(self, raw_price: Any) -> str:
        """تبدیل قیمت خام به قالب خوانا."""
        if raw_price is None or raw_price == "":
            return "ناموجود"

        try:
            normalized = self._normalize_digits(raw_price)
            digits = re.sub(r"[^\d]", "", normalized)

            if not digits:
                return "ناموجود"

            clean_num = int(digits)

            if clean_num <= 0:
                return "ناموجود"

            return f"{clean_num:,} تومان"

        except (ValueError, TypeError):
            return "ناموجود"

    @staticmethod
    def _first_value(*values: Any) -> Any:
        """برگرداندن اولین مقدار معتبر."""
        for value in values:
            if value is not None and value != "":
                return value
        return None

    def _extract_price(self, item: Dict[str, Any]) -> Any:
        """استخراج قیمت از ساختارهای مختلف داده محصول."""
        pricing = item.get("pricing")
        lowest_price = item.get("lowestPrice")
        price_variants = item.get("priceVariants")
        sellers = item.get("sellers")

        pricing_min_price = (
            pricing.get("minPrice")
            if isinstance(pricing, dict)
            else None
        )

        lowest_price_value = (
            lowest_price.get("price")
            if isinstance(lowest_price, dict)
            else None
        )

        first_variant_price = None
        if isinstance(price_variants, list) and price_variants:
            first_variant = price_variants[0]
            if isinstance(first_variant, dict):
                first_variant_price = self._first_value(
                    first_variant.get("price"),
                    first_variant.get("amount"),
                    first_variant.get("value"),
                )

        first_seller_price = None
        if isinstance(sellers, list) and sellers:
            first_seller = sellers[0]
            if isinstance(first_seller, dict):
                first_seller_price = self._first_value(
                    first_seller.get("price"),
                    first_seller.get("amount"),
                    first_seller.get("value"),
                )

        return self._first_value(
            item.get("minPrice"),
            item.get("cheapestPrice"),
            item.get("price"),
            pricing_min_price,
            lowest_price_value,
            first_variant_price,
            first_seller_price,
        )

    def _extract_json_products(self, page_props: Dict[str, Any]) -> List[Dict[str, Any]]:
        """استخراج محصولات از داده‌های JSON مربوط به Next.js."""
        raw_items = []

        dehydrated_state = page_props.get("dehydratedState", {})
        queries = (
            dehydrated_state.get("queries", [])
            if isinstance(dehydrated_state, dict)
            else []
        )

        for query in queries:
            if not isinstance(query, dict):
                continue

            state = query.get("state", {})
            state_data = (
                state.get("data", {})
                if isinstance(state, dict)
                else {}
            )

            if not isinstance(state_data, dict):
                continue

            results = state_data.get("results")
            items = state_data.get("items")

            if isinstance(results, list):
                raw_items = results
                break

            if isinstance(items, list):
                raw_items = items
                break

        if not raw_items:
            products_data = page_props.get("productsData", {})

            if isinstance(products_data, dict):
                raw_items = products_data.get("items") or []

            if not raw_items:
                raw_items = page_props.get("products", []) or []

        products = []
        seen_links = set()

        for item in raw_items:
            if not isinstance(item, dict):
                continue

            title = self._first_value(
                item.get("name"),
                item.get("title"),
                item.get("faName"),
                item.get("englishTitle"),
            )

            if not title:
                continue

            slug = self._first_value(
                item.get("slug"),
                item.get("id"),
            )

            link = (
                f"{self.BASE_URL}/product/{slug}/"
                if slug
                else ""
            )

            if link and link in seen_links:
                continue

            price_value = self._extract_price(item)

            products.append({
                "title": str(title).strip(),
                "price": self._format_price(price_value),
                "link": link,
            })

            if link:
                seen_links.add(link)

        return products

    def _parse_html_fallback(
        self,
        soup: BeautifulSoup,
        existing_products: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """استخراج محصولات از HTML در صورت نبود داده JSON."""
        products = existing_products or []
        seen_links = {
            product.get("link")
            for product in products
            if product.get("link")
        }

        product_links = soup.find_all(
            "a",
            href=re.compile(
                r"^/product/(?!list|compare|category|brand).*"
            ),
        )

        for link_element in product_links:
            href = link_element.get("href", "").strip()

            if not href:
                continue

            full_link = (
                f"{self.BASE_URL}{href}"
                if href.startswith("/")
                else href
            )

            clean_link = full_link.split("?", 1)[0]

            if clean_link in seen_links:
                continue

            heading = link_element.find(["h2", "h3", "h4", "p"])

            title = (
                heading.get_text(" ", strip=True)
                if heading
                else link_element.get_text(" ", strip=True)
            )

            if len(title) < 5:
                continue

            ignored_titles = {
                "مشاهده همه",
                "مقایسه",
                "خانه",
                "محصولات",
            }

            if title in ignored_titles:
                continue

            container = (
                link_element.find_parent("div")
                or link_element
            )

            container_text = container.get_text(" ", strip=True)

            price_match = re.search(
                r"(?:از\s*)?"
                r"([\d۰-۹٠-٩,،\s]{3,20})"
                r"\s*(?:تومان|تومن|ریال)",
                container_text,
            )

            price_text = "ناموجود"

            if price_match:
                price_text = self._format_price(
                    price_match.group(1)
                )

            products.append({
                "title": title,
                "price": price_text,
                "link": clean_link,
            })

            seen_links.add(clean_link)

        return products

    def parse_products(self, html_content: str) -> List[Dict[str, Any]]:
        """استخراج محصولات زومیت از JSON یا HTML."""
        if not html_content or not isinstance(html_content, str):
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        products = []

        script_tag = soup.find("script", id="__NEXT_DATA__")

        if script_tag:
            script_content = script_tag.string or script_tag.get_text(
                strip=True
            )

            if script_content:
                try:
                    raw_json = json.loads(script_content)

                    page_props = (
                        raw_json
                        .get("props", {})
                        .get("pageProps", {})
                    )

                    if isinstance(page_props, dict):
                        products = self._extract_json_products(
                            page_props
                        )

                except (json.JSONDecodeError, TypeError, AttributeError):
                    products = []

        if products:
            return products

        return self._parse_html_fallback(soup)
