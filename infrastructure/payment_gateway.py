class PaymentGateway:

    async def charge(self, payment_method: str, amount_cents: int) -> bool:
        print(f"Charging {amount_cents} cents via {payment_method}")
        return True

