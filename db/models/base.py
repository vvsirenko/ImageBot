import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, \
    String, Boolean, FLOAT, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

payment_status_enum = Enum("pending", "success", "failed", "refunded",
                           name="payment_status", create_type=False)
subscription_status_enum = Enum("active", "inactive", "expired",
                           name="subscription_status", create_type=False)
gender_enum = Enum("male", "female", name="gender", create_type=False)

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tg_id = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_premium = Column(Boolean, nullable=True)
    is_bot = Column(Boolean, nullable=True)
    discount_balance = Column(Numeric(3, 1), default=0.0)
    referral_link = Column(String, unique=True, default=False)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='SET NULL'))
    subscription_status = Column(subscription_status_enum, default="inactive")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    """
        referrer - создание связи один-ко-многим
        # Кто пригласил этого пользователя:
            inviter = user.referrer  
        # Все, кого пригласил этот пользователь:
            referrals = user.referrals_made 
    """
    referrer = relationship('User', remote_side=[user_id], backref='referrals_made')

    """
    Эта строка создаёт связь "один-ко-многим" между пользователем и реферальными записями, где он является приглашающим:
        'Referral' - указывает на модель Referral
        foreign_keys='Referral.referrer_id' - явно указывает, какой внешний ключ использовать
        back_populates='referrer' - синхронизирует связь с атрибутом referrer в модели Referral
    """
    referred_users = relationship('Referral', foreign_keys='Referral.referrer_id', back_populates='referrer')
    """
    Эта строка создаёт связь "один-ко-многим" между пользователем и реферальными записями, где он является приглашённым:
        'Referral' - указывает на модель Referral
        foreign_keys='Referral.referred_id' - явно указывает, какой внешний ключ использовать
        back_populates='referred' - синхронизирует связь с атрибутом referred в модели Referral
    """
    referrals_received = relationship('Referral', foreign_keys='Referral.referred_id', back_populates='referred')


    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    referred_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    bonus_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    referrer = relationship('User', foreign_keys=[referrer_id], back_populates='referred_users')
    referred = relationship('User', foreign_keys=[referred_id], back_populates='referrals_received')

    # UNUQUE CHECK
    __table_args__ = (
        UniqueConstraint('referrer_id', 'referred_id',
                         name='_referrer_referred_uc'),
    )




class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False)
    payment_status = Column(payment_status_enum, default="pending")
    referrer_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    referrer = relationship("User", foreign_keys=[user_id], backref='referrals_made')

class Style(Base):
    __tablename__ = "styles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    gender = Column(gender_enum, nullable=False)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PromoCode(Base):
    __tablename__ = "promo_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)

