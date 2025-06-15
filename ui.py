# ============================================================
# file: ui.py
# TUI(CLI) 인터페이스
# ============================================================

import os
from inventory import InventoryManager
from payment import PaymentProcessor
from report import ReportManager

ADMIN_PW = "admin123"


class UserInterface:
    """TUI 기반 입·출력 컨트롤러"""
    def __init__(self):
        self.inv   = InventoryManager()
        self.pay   = PaymentProcessor()
        self.rep   = ReportManager()

    # --------------------------------------------------------
    # 유틸: CLS / PAUSE
    # --------------------------------------------------------
    @staticmethod
    def _cls()   -> None: os.system("cls" if os.name == "nt" else "clear")
    @staticmethod
    def _pause() -> None: input("\n계속하려면 Enter...")

    # --------------------------------------------------------
    def run(self) -> None:
        while True:
            self._cls()
            print("=== 🍹 음료 자동판매기 ===")
            for p in self.inv.list_products():
                status = "품절" if p["stock"] <= 0 else f"{p['price']}원"
                print(f"[{p['id']}] {p['name']:<6} — {status}")
            print("\n[a] 관리자 모드   [q] 종료")
            sel = input("👉 선택: ").strip().lower()

            if sel == "q":
                print("안녕히 가세요!")
                break
            if sel == "a":
                self._admin_mode()
                continue
            if not sel.isdigit():
                print("⚠️ 잘못된 입력입니다.")
                self._pause(); continue

            pid = int(sel)
            prod = self.inv.get_product(pid)
            if not prod:
                print("⚠️ 존재하지 않는 상품입니다.")
                self._pause(); continue
            if prod["stock"] <= 0:
                print("⚠️ 품절된 상품입니다.")
                self._pause(); continue

            # 결제
            print(f"\n선택: {prod['name']} ({prod['price']}원)")
            try:
                inserted = int(input("투입 금액(원): ").strip())
            except ValueError:
                print("⚠️ 숫자로 입력해 주세요.")
                self._pause(); continue

            ok, result = self.pay.pay(prod["price"], inserted)
            if not ok:
                print(f"잔액이 {result}원 부족합니다. 거래가 취소되었습니다.")
                self._pause(); continue

            change_map: dict[int, int] = result  # type: ignore
            self.inv.update_stock(pid, -1)
            self.rep.record_sale(prod["name"], prod["price"])

            print(f"\n✅ '{prod['name']}' 나왔습니다! 잔돈:")
            if not change_map:
                print("  (없음)")
            else:
                for coin, cnt in change_map.items():
                    print(f"  {coin}원 × {cnt}개")
            self._pause()

    # --------------------------------------------------------
    # 관리자 메뉴
    # --------------------------------------------------------
    def _admin_mode(self) -> None:
        if input("관리자 암호: ").strip() != ADMIN_PW:
            print("❌ 암호가 틀렸습니다."); self._pause(); return
        while True:
            self._cls()
            print("=== 🔧 관리자 메뉴 ===")
            print("[1] 재고·가격 수정")
            print("[2] 주간 매출 그래프 생성")
            print("[b] 이전 메뉴")
            cmd = input("👉 선택: ").strip().lower()
            if cmd == "b": break
            if cmd == "1": self._edit_product()
            elif cmd == "2":
                path = self.rep.plot_hourly_sales()
                if path: print(f"✅ 그래프가 '{path}' 로 저장되었습니다.")
                self._pause()
            else:
                print("⚠️ 잘못된 입력입니다."); self._pause()

    def _edit_product(self) -> None:
        try:
            pid = int(input("수정할 상품 ID: ").strip())
            p   = self.inv.get_product(pid)
            if not p:
                print("⚠️ 잘못된 ID"); self._pause(); return
            print(f"현재 [{pid}] {p['name']}: {p['price']}원 / 재고 {p['stock']}개")
            new_p = input("새 가격(Enter: 건너뜀): ").strip()
            new_s = input("새 재고(Enter: 건너뜀): ").strip()
            self.inv.update_product(
                pid,
                price=int(new_p) if new_p else None,
                stock=int(new_s) if new_s else None)
            print("✅ 수정 완료!")
        except ValueError:
            print("⚠️ 숫자로 입력해 주세요.")
        finally:
            self._pause()
