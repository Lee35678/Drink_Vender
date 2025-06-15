# ============================================================
# file: report.py
# 하루(오늘) 매출 관리 모듈 – CSV 기록 + 시간별 그래프
# ============================================================

import csv
import os
import time            # 날짜‧시간 처리에 표준 time 모듈 사용

try:
    import matplotlib.pyplot as plt   # 그래프용(선택 설치)
except ImportError:
    plt = None

SALES_CSV  = "sales.csv"
GRAPH_FILE = "hourly_sales.png"


class ReportManager:
    """하루(오늘) 매출 기록 및 리포트 생성"""
    def __init__(self, csv_path: str = SALES_CSV):
        self.csv_path = csv_path

        # 파일이 없다면 헤더 생성: date, hour, product, price
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["date", "hour", "product", "price"])

    # --------------------------------------------------------
    # 판매 한 건을 CSV 에 기록
    # --------------------------------------------------------
    def record_sale(self, product_name: str, price: int) -> None:
        now_struct = time.localtime()                        # 현재 로컬 시간
        today      = time.strftime("%Y-%m-%d", now_struct)   # YYYY-MM-DD
        hour       = time.strftime("%H",      now_struct)    # '00'~'23'

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([today, hour, product_name, price])

    # --------------------------------------------------------
    # 오늘 하루 매출을 '시간 → 금액 합계' 딕셔너리로 반환
    # --------------------------------------------------------
    def hourly_summary(self) -> dict[int, int]:
        """
        예) {0: 1500, 1: 0, 2: 3500, …, 23: 0}
        모든 시간대(0~23시)를 키로 갖고, 매출 없는 시각은 0으로 채움
        """
        today = time.strftime("%Y-%m-%d", time.localtime())
        summary: dict[int, int] = {h: 0 for h in range(24)}  # 기본값 0

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("date") != today:
                    continue
                try:
                    hour = int(row.get("hour", "0"))
                    price = int(row.get("price", "0"))
                except ValueError:
                    continue
                if 0 <= hour <= 23:
                    summary[hour] += price
        return summary

    # --------------------------------------------------------
    # 시간별 막대그래프 생성(PNG) – matplotlib 설치 시
    # --------------------------------------------------------
    def plot_hourly_sales(self) -> str | None:
        """
        성공 시 파일 경로 반환, matplotlib 미설치·데이터 없음 시 None
        """
        if plt is None:
            print("⚠️ matplotlib 미설치 – 그래프 생성을 건너뜁니다.")
            return None

        data = self.hourly_summary()
        if not any(data.values()):
            print("⚠️ 오늘 매출 데이터가 없습니다.")
            return None

        hours = list(range(24))
        sales = [data[h] for h in hours]

        plt.figure()
        plt.bar(hours, sales)
        plt.xticks(hours)                       # 0,1,2,…23 라벨 표시
        plt.xlabel("time (hour)")
        plt.ylabel("Sales (KRW)")
        plt.title("Sales by time period")
        plt.tight_layout()
        plt.savefig(GRAPH_FILE, dpi=150, bbox_inches="tight")
        plt.close()

        return GRAPH_FILE
