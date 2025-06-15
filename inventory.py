# ============================================================
# file: inventory.py
# 재고 관리 모듈 – CSV 로부터 상품 정보를 불러오고 저장
# ============================================================

import csv
import os

PRODUCT_CSV = "products.csv"


class InventoryManager:
    """상품 정보를 관리하는 클래스"""
    def __init__(self, csv_path: str = PRODUCT_CSV):
        self.csv_path = csv_path
        self.products: list[dict] = []       # List, Dict 대신 내장 list/dict 제너릭 사용
        self._load_or_init()

    # --------------------------------------------------------
    # 내부 편의 메서드
    # --------------------------------------------------------
    def _load_or_init(self) -> None:
        """CSV 가 존재하면 읽고, 없으면 기본값으로 초기화"""
        if os.path.exists(self.csv_path):
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.products = [
                    {"id": int(r["id"]),
                     "name": r["name"],
                     "price": int(r["price"]),
                     "stock": int(r["stock"])}
                    for r in reader
                ]
        else:
            # 최소 5종 기본 음료
            self.products = [
                {"id": 1, "name": "콜라",   "price": 1500, "stock": 10},
                {"id": 2, "name": "사이다", "price": 1500, "stock": 10},
                {"id": 3, "name": "커피",   "price": 2000, "stock": 10},
                {"id": 4, "name": "주스",   "price": 1800, "stock": 10},
                {"id": 5, "name": "생수",   "price": 1000, "stock": 10},
            ]
            self.save()                       # 첫 실행 시 CSV 생성

    def save(self) -> None:
        """현재 products 리스트를 CSV 로 저장"""
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "price", "stock"])
            writer.writeheader()
            writer.writerows(self.products)

    # --------------------------------------------------------
    # 외부 API
    # --------------------------------------------------------
    def list_products(self) -> list[dict]:
        return self.products

    def get_product(self, pid: int) -> dict | None:
        return next((p for p in self.products if p["id"] == pid), None)

    def update_stock(self, pid: int, delta: int) -> None:
        prod = self.get_product(pid)
        if prod:
            prod["stock"] += delta
            self.save()

    def update_product(self, pid: int,
                       *, price: int | None = None, stock: int | None = None) -> bool:
        prod = self.get_product(pid)
        if not prod:
            return False
        if price is not None:
            prod["price"] = price
        if stock is not None:
            prod["stock"] = stock
        self.save()
        return True
