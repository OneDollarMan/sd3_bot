from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, BigInteger, func, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class TelegramUser(Base):
    __tablename__ = 'telegram_user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(Text, nullable=True)

    image_requests: Mapped[list['ImageRequest']] = relationship(back_populates='user')


class ImageRequest(Base):
    __tablename__ = 'image_request'

    STATUS_NOT_STARTED = "NOT_STARTED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_FINISHED = "FINISHED"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('telegram_user.id'))
    status: Mapped[str] = mapped_column(Text, server_default=STATUS_NOT_STARTED)
    prompt: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped['TelegramUser'] = relationship(back_populates='image_requests')
