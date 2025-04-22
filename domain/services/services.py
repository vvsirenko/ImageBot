from domain.subscription import Subscription
from infrastructure.payment_gateway import PaymentGateway
from infrastructure.user_repository import AbcUserRepository


class PaymentService:

    def __init__(
            self,
             payment_gateway: PaymentGateway,
             user_repo: AbcUserRepository
    ):
        self.payment_gateway = payment_gateway
        self.user_repo = user_repo

    def purchase_plan(self, user_id, plan: Subscription, payment_method: str):
        user = self.user_repo.fetch_profile(user_id)
        #todo add get user

        success = self.payment_gateway.charge(payment_method, plan.price)
        if not success:
            raise Exception("Payment was declined.")

        user.image_limit += plan.image_count
        self.user_repo.save(user)
        return user