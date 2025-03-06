import aiohttp


class FastAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url

    async def process_image(self, data: dict):
        return await self.__process_image(data)

    async def __process_image(self, data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/process_image/", json=data) as response:
                    response.raise_for_status()
                    image_bytes = await response.content.read()
                    status = response.status
                    return {"status": status, "content": image_bytes}
        except Exception as e:
            return

