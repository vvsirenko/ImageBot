from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    referral_link = Column(String, unique=True, nullable=False)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    referrals = relationship('Referral', back_populates='referrer')
    referred_by = relationship('User', remote_side=[user_id], backref='referred_users')


class Image(Base):
    __tablename__ = 'images'
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    original_image_url = Column(String, nullable=False)
    processed_image_url = Column(String, nullable=True)
    style_id = Column(UUID(as_uuid=True), ForeignKey('styles.style_id'), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'failed', name='image_status'), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', backref='images')
    style = relationship('Style', backref='images')


class Style(Base):
    __tablename__ = 'styles'
    style_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    style_name = Column(String, nullable=False)
    style_description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Referral(Base):
    __tablename__ = 'referrals'
    referral_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    referrer = relationship('User', foreign_keys=[referrer_id], back_populates='referrals')
    referred = relationship('User', foreign_keys=[referred_id], backref='referred_by')


class Promocode(Base):
    __tablename__ = 'promocodes'
    promocode_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    discount_amount = Column(Float, nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(Base):
    __tablename__ = 'payments'
    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    payment_status = Column(Enum('pending', 'completed', 'failed', name='payment_status'), default='pending')
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', backref='payments')