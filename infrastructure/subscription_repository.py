import abc

import aiohttp
import logging
from domain.models import BaseResponse
from domain.subscription import Subscription

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class AbcSubscriptionRepository(abc.ABC):

    @abc.abstractmethod
    async def save(self, subscription: Subscription):
        ...

    @abc.abstractmethod
    async def get_by_id(self, sub_id: str):
         ...


class SubscriptionRepository(AbcSubscriptionRepository):
    def __init__(self, base_url):
        self.base_url = base_url

    async def save(self, subscription: Subscription):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=f"{self.base_url}/save_subscription/", json=subscription.to_dict()
                ) as response:
                    response.raise_for_status()
                    return BaseResponse(**await response.json())
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {subscription.user_id}"
            )
            return BaseResponse.fail(
                error=f"Unexpected error: {e}",
                message=f"User_id: {subscription.user_id}"
            )