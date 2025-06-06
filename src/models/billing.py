"""
Billing and Payment Models
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship
import json

from .base import db, BaseModel


class Invoice(BaseModel):
    """Invoice model"""

    __tablename__ = "invoices"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)

    # Invoice details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="USD")

    # Status
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, paid, failed, cancelled

    # Dates
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)

    # Billing period
    billing_period_start = db.Column(db.DateTime)
    billing_period_end = db.Column(db.DateTime)

    # Payment info
    stripe_invoice_id = db.Column(db.String(255), unique=True)
    payment_method = db.Column(db.String(50))

    # Invoice items (JSON)
    line_items = db.Column(db.JSON)

    # Relationships
    user = relationship("User", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.invoice_number:
            self.generate_invoice_number()

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.invoice_number = f"INV-{timestamp}-{self.user_id}"

    def mark_paid(self, payment_date=None):
        """Mark invoice as paid"""
        self.status = "paid"
        self.paid_date = payment_date or datetime.utcnow()
        self.save()

    def mark_failed(self):
        """Mark invoice as failed"""
        self.status = "failed"
        self.save()

    def mark_cancelled(self):
        """Mark invoice as cancelled"""
        self.status = "cancelled"
        self.save()

    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.due_date < datetime.utcnow() and self.status == "pending"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "invoice_number": self.invoice_number,
            "amount": float(self.amount),
            "tax_amount": float(self.tax_amount),
            "total_amount": float(self.total_amount),
            "currency": self.currency,
            "status": self.status,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            "billing_period_start": (
                self.billing_period_start.isoformat()
                if self.billing_period_start
                else None
            ),
            "billing_period_end": (
                self.billing_period_end.isoformat() if self.billing_period_end else None
            ),
            "stripe_invoice_id": self.stripe_invoice_id,
            "payment_method": self.payment_method,
            "line_items": self.line_items,
            "is_overdue": self.is_overdue(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Payment(BaseModel):
    """Payment model"""

    __tablename__ = "payments"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))

    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="USD")
    payment_method = db.Column(db.String(50), nullable=False)

    # Status
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, completed, failed, refunded

    # External payment info
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_charge_id = db.Column(db.String(255))
    transaction_id = db.Column(db.String(255))

    # Dates
    payment_date = db.Column(db.DateTime)
    refund_date = db.Column(db.DateTime)

    # Additional info
    description = db.Column(db.Text)
    payment_metadata = db.Column(db.JSON)

    # Relationships
    user = relationship("User", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

    def mark_completed(self, payment_date=None):
        """Mark payment as completed"""
        self.status = "completed"
        self.payment_date = payment_date or datetime.utcnow()
        self.save()

        # Mark associated invoice as paid
        if self.invoice:
            self.invoice.mark_paid(self.payment_date)

    def mark_failed(self):
        """Mark payment as failed"""
        self.status = "failed"
        self.save()

        # Mark associated invoice as failed
        if self.invoice:
            self.invoice.mark_failed()

    def mark_refunded(self, refund_date=None):
        """Mark payment as refunded"""
        self.status = "refunded"
        self.refund_date = refund_date or datetime.utcnow()
        self.save()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "invoice_id": self.invoice_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "stripe_payment_intent_id": self.stripe_payment_intent_id,
            "stripe_charge_id": self.stripe_charge_id,
            "transaction_id": self.transaction_id,
            "payment_date": (
                self.payment_date.isoformat() if self.payment_date else None
            ),
            "refund_date": self.refund_date.isoformat() if self.refund_date else None,
            "description": self.description,
            "metadata": self.payment_metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BillingAddress(BaseModel):
    """User billing address"""

    __tablename__ = "billing_addresses"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    # Address details
    company_name = db.Column(db.String(255))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    # Tax info
    tax_id = db.Column(db.String(50))
    vat_number = db.Column(db.String(50))

    # Relationships
    user = relationship("User")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "tax_id": self.tax_id,
            "vat_number": self.vat_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
