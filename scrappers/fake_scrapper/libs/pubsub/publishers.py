from redis.asyncio.client import PubSub


class IPublisher:
    async def publish(self, msg):
        ...


class RedisPublisher(IPublisher):
    def __init__(
        self,
        pub_channel,
        pubsub: PubSub,
    ):
        self.channel = pub_channel
        self.pubsub = pubsub

    async def publish(self, msg):
        await self.pubsub.execute_command('PUBLISH', self.channel, msg)
