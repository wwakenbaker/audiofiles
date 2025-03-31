from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    access_token: Mapped[str] = mapped_column(unique=True)
    refresh_token: Mapped[str] = mapped_column(unique=True)
    grade: Mapped[str] = mapped_column(default="User")

    audio_files = relationship("AudioFile", back_populates="owner")


class AudioFile(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(unique=True, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(unique=True)
    file_path: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    owner = relationship("User", back_populates="audio_files")
