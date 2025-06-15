# ============================================================
# file: payment.py
# 결제 처리 모듈 – 잔돈 최소 동전 계산
# ============================================================

COINS = (500, 100, 50, 10)                  # 큰 금액부터 Greedy 로 계산


class PaymentProcessor:
    """투입 금액과 잔돈 계산 담당"""
    def __init__(self, coin_kinds: tuple[int, ...] = COINS):
        self.coin_kinds = coin_kinds

    # --------------------------------------------------------
    def calculate_change(self, change: int) -> dict[int, int]:
        """거스름돈을 최소 동전 수로 환산 → {동전: 개수}"""
        coin_map: dict[int, int] = {}
        for coin in self.coin_kinds:
            cnt, change = divmod(change, coin)
            if cnt:
                coin_map[coin] = cnt
        return coin_map

    def pay(self, price: int, inserted: int) -> tuple[bool, int | dict[int, int]]:
        """
        결제 시도 → (성공 여부, 잔돈 dict 또는 부족액 int) 반환
        """
        if inserted < price:
            return False, price - inserted
        change = inserted - price
        return True, self.calculate_change(change)
