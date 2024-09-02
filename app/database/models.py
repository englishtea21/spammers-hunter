from sqlalchemy import (
    DateTime,
    Float,
    String,
    Text,
    BigInteger,
    Boolean,
    Enum as SqlaEnum,
    func,
)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum
import datetime


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


# an instance of banned user
class BannedUser(Base):
    __tablename__ = "banned_users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("antispam_chats.chat_id")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    banned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    banned_till: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    chat: Mapped["AntiSpamChat"] = relationship(
        "AntiSpamChat", back_populates="banned_users"
    )


# an instance of muted user
class MutedUser(Base):
    __tablename__ = "muted_users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("antispam_chats.chat_id")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    muted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    muted_till: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    chat: Mapped["AntiSpamChat"] = relationship(
        "AntiSpamChat", back_populates="muted_users"
    )


# punishment for spam
class Punishment(Enum):
    BAN = 0
    MUTE = 1


# an instance of chat administrator who are provided with the control panel
class ChatAdmin(Base):
    __tablename__ = "chats_admins"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("antispam_chats.chat_id")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat: Mapped["AntiSpamChat"] = relationship(
        "AntiSpamChat", back_populates="chat_admins"
    )


# an instance of chat where antispam bot works
class AntiSpamChat(Base):
    __tablename__ = "antispam_chats"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    punishment: Mapped[Punishment] = mapped_column(
        SqlaEnum(Punishment), default=Punishment.MUTE
    )
    
    # The duration of the punishment is determined by the number of hours provided.
    # If the punishment is for an indefinite period, it will be indicated as "none".
    punishment_duration: Mapped[int] = mapped_column(
        BigInteger, nullable=True, default=24
    )

    banned_users: Mapped[list[BannedUser]] = relationship(
        "BannedUser", back_populates="chat"
    )
    muted_users: Mapped[list[MutedUser]] = relationship(
        "MutedUser", back_populates="chat"
    )
    chat_admins: Mapped[list[ChatAdmin]] = relationship(
        "ChatAdmin", back_populates="chat"
    )
