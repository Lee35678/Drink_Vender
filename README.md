# Drink_Vender

Python으로 만든 음료 자판기 프로그램으로, 터미널(CLI) 화면과 Tkinter GUI 화면을 동시에 띄워 구매·재고 관리·매출 그래프 기능을 제공합니다.

## 개요

음료 선택 → 금액 투입 → 잔돈 계산 → 재고 차감 → 매출 기록으로 이어지는 자판기 흐름을 구현한 프로그램입니다.
재고 관리(`inventory.py`), 결제(`payment.py`), 매출 기록(`report.py`)을 모듈로 나누고, 같은 모듈을 텍스트 화면(`ui.py`)과 GUI(`gui.py`)가 함께 사용합니다.
상품과 매출 데이터는 CSV 파일에 저장해 프로그램을 다시 켜도 유지됩니다.

## 주요 기능

- **상품 구매**: 상품 선택 후 투입 금액 입력, 금액이 부족하면 부족액을 알려 주고 거래 취소
- **잔돈 계산**: 500·100·50·10원 동전으로 개수가 가장 적게 나오도록(큰 동전부터) 거스름돈 계산
- **품절 처리**: 재고가 0이면 CLI에서는 "품절" 표시, GUI에서는 버튼 비활성화
- **관리자 모드** (암호 확인 후 진입)
  - 상품별 가격·재고 수정
  - 오늘 매출을 시간대(0~23시)별로 합산한 막대그래프를 `hourly_sales.png`로 저장 (matplotlib 필요)
- **데이터 저장**: 상품 목록은 `products.csv`, 판매 기록은 `sales.csv`(날짜, 시, 상품, 가격)에 저장
- 첫 실행 시 기본 음료 5종(콜라·사이다·커피·주스·생수, 재고 각 10개)으로 `products.csv` 생성

## 시스템 구성

```
main.py
 ├─ CLIThread (데몬 스레드) ── ui.py  UserInterface ─┐
 └─ 메인 스레드 ───────────── gui.py GUIInterface  ─┤  (각자 인스턴스 생성)
                                                     ├─ inventory.py  InventoryManager ── products.csv
                                                     ├─ payment.py    PaymentProcessor (잔돈 계산)
                                                     └─ report.py     ReportManager   ── sales.csv, hourly_sales.png
```

Tkinter는 메인 스레드에서만 동작하므로 GUI를 메인 스레드에, CLI를 데몬 스레드에 두었고, GUI 창을 닫으면 CLI도 함께 종료됩니다.

## 기술 스택

- Python 3.10 이상 (`int | None` 같은 타입 표기 사용)
- Tkinter (GUI, 표준 라이브러리)
- csv, threading (표준 라이브러리)
- matplotlib (선택, 매출 그래프용)

## 실행 방법

```bash
pip install matplotlib   # 선택: 매출 그래프를 만들 때만 필요
python main.py
```

- 실행한 폴더에 `products.csv`, `sales.csv`, `hourly_sales.png`가 만들어집니다.
- 실행하면 터미널에 CLI 메뉴가, 별도 창에 GUI가 함께 뜹니다.
- 관리자 암호는 `gui.py`, `ui.py`의 `ADMIN_PW` 상수에 정의되어 있습니다.

## 폴더 구조

```
Drink_Vender/
├── main.py          # 진입점: CLI 스레드 + GUI 동시 실행
├── gui.py           # Tkinter GUI (상품 버튼, 관리자 창)
├── ui.py            # 텍스트 기반 CLI
├── inventory.py     # 상품·재고 관리 (products.csv)
├── payment.py       # 결제·잔돈 계산
├── report.py        # 매출 기록·시간대별 그래프 (sales.csv)
├── image.png        # 자판기 화면 이미지 (현재 코드의 GUI 화면과는 다름)
└── __pycache__/     # Python 바이트코드 캐시 (커밋됨)
```

## 참고

코드에서 확인되는 한계입니다.

- **CLI와 GUI가 상태를 공유하지 않음**: 두 화면이 각자 `InventoryManager`를 만들어 메모리에 따로 들고 있습니다. 한쪽에서 구매하면 CSV에는 저장되지만 다른 쪽 화면에는 반영되지 않고, 이후 다른 쪽이 저장하면 앞의 변경을 덮어쓸 수 있습니다.
- **결제 방식**: 투입 금액을 숫자로 한 번 입력하는 방식이며, 동전/지폐 단위 투입이나 자판기 내 거스름돈 보유량은 다루지 않습니다.
- **관리자 암호**가 소스 코드에 평문으로 들어 있습니다.
- CLI 관리자 메뉴의 "주간 매출 그래프 생성" 항목은 실제로는 **오늘의 시간대별** 그래프를 만듭니다.
- 가격·재고 수정 시 음수 값 검사가 없습니다.
- `image.png`는 상품 구성(20여 종)과 카드 결제 버튼 등이 현재 코드와 다르므로, 이 코드의 실행 화면이 아닙니다.
