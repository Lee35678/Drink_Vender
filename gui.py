# ============================================================
# file: gui.py
# Tkinter 기반 GUI 인터페이스
# ============================================================

import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# 기존 모듈 재사용
from inventory import InventoryManager
from payment import PaymentProcessor
from report import ReportManager

ADMIN_PW = "admin123"          # 🔒 관리자 암호


class GUIInterface:
    """그래픽 사용자 인터페이스"""
    def __init__(self):
        # 핵심 로직 인스턴스
        self.inv  = InventoryManager()
        self.pay  = PaymentProcessor()
        self.rep  = ReportManager()

        # Tk 루트 창
        self.root = tk.Tk()
        self.root.title("🍹 음료 자동판매기")

        # 메뉴바(관리자)
        menubar = tk.Menu(self.root)
        admin_menu = tk.Menu(menubar, tearoff=0)
        admin_menu.add_command(label="관리자 모드", command=self._open_admin)
        menubar.add_cascade(label="관리", menu=admin_menu)
        self.root.config(menu=menubar)

        # 상품 버튼용 프레임
        self.products_frame = ttk.Frame(self.root, padding=10)
        self.products_frame.grid(row=0, column=0)

        # 최초 버튼 생성
        self._draw_product_buttons()

        self.root.mainloop()

    # --------------------------------------------------------
    # 상품 버튼 그리기 / 갱신
    # --------------------------------------------------------
    def _draw_product_buttons(self) -> None:
        """상품 목록을 버튼으로 나열"""
        # 기존 버튼 제거
        for child in self.products_frame.winfo_children():
            child.destroy()

        products = self.inv.list_products()
        for idx, prod in enumerate(products):
            row, col = divmod(idx, 3)     # 3열 그리드 배치
            text = f"{prod['name']}\n{prod['price']}원"
            state = tk.DISABLED if prod["stock"] <= 0 else tk.NORMAL
            btn = ttk.Button(
                self.products_frame,
                text=text,
                width=15,
                state=state,
                command=lambda pid=prod["id"]: self._purchase(pid)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

    # --------------------------------------------------------
    # 결제 프로세스
    # --------------------------------------------------------
    def _purchase(self, pid: int) -> None:
        """상품 버튼 클릭 시 호출"""
        prod = self.inv.get_product(pid)
        if not prod:
            messagebox.showerror("오류", "상품 정보를 찾을 수 없습니다.")
            return

        # 투입 금액 입력
        inserted = simpledialog.askinteger(
            "금액 투입",
            f"[{prod['name']}] 가격: {prod['price']}원\n\n투입 금액(원)을 입력하세요:",
            minvalue=0
        )
        if inserted is None:
            return  # 취소

        ok, result = self.pay.pay(prod["price"], inserted)
        if not ok:
            messagebox.showwarning("잔액 부족", f"{result}원이 부족합니다. 거래 취소!")
            return

        # 재고‧매출 처리
        self.inv.update_stock(pid, -1)
        self.rep.record_sale(prod["name"], prod["price"])
        self._draw_product_buttons()      # 버튼 상태 갱신

        # 잔돈 안내
        change_map: dict = result         # type: ignore
        if not change_map:
            msg = "잔돈 없이 결제가 완료되었습니다."
        else:
            parts = [f"{c}원 × {cnt}개" for c, cnt in change_map.items()]
            msg = "잔돈:\n" + "\n".join(parts)
        messagebox.showinfo("구매 완료", f"'{prod['name']}' 나왔습니다!\n\n{msg}")

    # --------------------------------------------------------
    # 관리자 모드
    # --------------------------------------------------------
    def _open_admin(self) -> None:
        """암호 확인 후 관리자 창 오픈"""
        pw = simpledialog.askstring("관리자 암호", "암호를 입력하세요:", show="*")
        if pw != ADMIN_PW:
            messagebox.showerror("접근 거부", "암호가 틀렸습니다.")
            return

        AdminWindow(self.root, self.inv, self.rep, redraw_products=self._draw_product_buttons)


class AdminWindow(tk.Toplevel):
    """관리자 전용 설정 창"""
    def __init__(self, master, inv, rep, *, redraw_products):
        super().__init__(master)
        self.title("🔧 관리자 패널")
        self.inv = inv
        self.rep = rep
        self.redraw_products = redraw_products

        # 상품 리스트
        self.listbox = tk.Listbox(self, width=25, height=10)
        self.listbox.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
        self._fill_listbox()
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # 상세 수정 영역
        ttk.Label(self, text="가격(원)").grid(row=0, column=1, sticky="w")
        self.price_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.price_var, width=10).grid(row=0, column=2)

        ttk.Label(self, text="재고(개)").grid(row=1, column=1, sticky="w")
        self.stock_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.stock_var, width=10).grid(row=1, column=2)

        ttk.Button(self, text="수정 저장", command=self._save_changes).grid(row=2, column=1, columnspan=2, pady=5)
        ttk.Button(self, text="오늘 시간별 매출 그래프", command=self._make_graph).grid(row=3, column=1, columnspan=2)

    # --------------------------------------------------------
    def _fill_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.inv.list_products():
            self.listbox.insert(tk.END, f"[{p['id']}] {p['name']}")

    def _on_select(self, _evt):
        sel = self.listbox.curselection()
        if not sel:
            return
        txt = self.listbox.get(sel[0])
        pid = int(txt.split("]")[0][1:])
        prod = self.inv.get_product(pid)
        if prod:
            self.price_var.set(str(prod["price"]))
            self.stock_var.set(str(prod["stock"]))
            self.current_pid = pid
        else:
            self.current_pid = None

    def _save_changes(self):
        if getattr(self, "current_pid", None) is None:
            messagebox.showwarning("선택 필요", "수정할 상품을 먼저 선택하세요.")
            return
        try:
            new_price = int(self.price_var.get())
            new_stock = int(self.stock_var.get())
        except ValueError:
            messagebox.showerror("입력 오류", "숫자로 입력해 주세요.")
            return
        self.inv.update_product(self.current_pid, price=new_price, stock=new_stock)
        messagebox.showinfo("완료", "수정이 저장되었습니다.")
        self.redraw_products()
        self._fill_listbox()

    def _make_graph(self):
        path = self.rep.plot_hourly_sales()
        if path:
            messagebox.showinfo("완료", f"그래프가 '{path}' 로 저장되었습니다.")
        else:
            messagebox.showwarning("실패", "그래프를 생성할 수 없습니다.")
