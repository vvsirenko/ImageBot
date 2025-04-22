from application.use_cases.create_avatar import UseCase
from domain.services.services import PaymentService
from domain.subscription import Subscription


class PaymentUseCase(UseCase):

    def __init__(
            self,
            payment_service: PaymentService
    ):
        self.payment_service = payment_service

    async def execute(self, user_id, sub_id, payment_method):
        plan = await self._get_plan_by_id(sub_id)
        return self.payment_service.purchase_plan(user_id, plan, payment_method)

    async def _get_plan_by_id(self, sub_id):
        sub = {
            "basic": Subscription(id="1", name="Basic", image_count=10, price=500),
            "pro": Subscription(id="2", name="Pro", image_count=50, price=2000),
            "ultra": Subscription(id="3", name="Ultra", image_count=100, price=3500),
        }
        return sub.get(sub_id)
