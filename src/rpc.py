import aio_pika
from aio_pika.patterns import Master
from config import RABBITMQ_URL, REQUEST_JOB_NAME
from src.schemas import ImageRequestSchema


async def create_image_request_task(request: ImageRequestSchema):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        master = Master(channel)
        await channel.declare_queue(REQUEST_JOB_NAME)
        await master.create_task(
            REQUEST_JOB_NAME, kwargs=dict(request=request),
        )
