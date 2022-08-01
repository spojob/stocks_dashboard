import asyncio
from redis.asyncio.client import PubSub


class ISubscriber:
    async def receive(self) -> str:
        ...


class RedisSubscriber(ISubscriber):
    def __init__(
        self,
        sub_channel,
        pubsub_pool: PubSub
    ) -> None:
        self.channel = sub_channel
        self.pubsub: PubSub = pubsub_pool

    async def receive(self) -> str:
        async with self.pubsub as p:
            await p.subscribe(self.channel)
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    yield message["data"]
                await asyncio.sleep(0)
                
