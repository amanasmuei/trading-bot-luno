"""
Billing and Payment API Endpoints
"""

from flask import Blueprint, request, jsonify, g
import logging

from src.auth.decorators import login_required, admin_required
from src.models.billing import Invoice, Payment, BillingAddress
from src.models.base import db

logger = logging.getLogger(__name__)

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')


@billing_bp.route('/invoices', methods=['GET'])
@login_required
def get_invoices():
    """Get user invoices"""
    try:
        user = g.current_user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Invoice.query.filter_by(user_id=user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        invoices = query.order_by(Invoice.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invoices.total,
                'pages': invoices.pages,
                'has_next': invoices.has_next,
                'has_prev': invoices.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get invoices error: {e}")
        return jsonify({'error': 'Failed to get invoices'}), 500


@billing_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    """Get specific invoice"""
    try:
        user = g.current_user
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get invoice error: {e}")
        return jsonify({'error': 'Failed to get invoice'}), 500


@billing_bp.route('/payments', methods=['GET'])
@login_required
def get_payments():
    """Get user payments"""
    try:
        user = g.current_user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        payments = Payment.query.filter_by(user_id=user.id).order_by(
            Payment.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': payments.total,
                'pages': payments.pages,
                'has_next': payments.has_next,
                'has_prev': payments.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get payments error: {e}")
        return jsonify({'error': 'Failed to get payments'}), 500


@billing_bp.route('/address', methods=['GET'])
@login_required
def get_billing_address():
    """Get user billing address"""
    try:
        user = g.current_user
        address = BillingAddress.query.filter_by(user_id=user.id).first()
        
        return jsonify({
            'address': address.to_dict() if address else None
        }), 200
        
    except Exception as e:
        logger.error(f"Get billing address error: {e}")
        return jsonify({'error': 'Failed to get billing address'}), 500


@billing_bp.route('/address', methods=['POST'])
@login_required
def create_billing_address():
    """Create or update billing address"""
    try:
        user = g.current_user
        data = request.get_json()
        
        required_fields = ['first_name', 'last_name', 'address_line_1', 'city', 'postal_code', 'country']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if address already exists
        address = BillingAddress.query.filter_by(user_id=user.id).first()
        
        if address:
            # Update existing address
            for field in ['company_name', 'first_name', 'last_name', 'address_line_1', 
                         'address_line_2', 'city', 'state', 'postal_code', 'country', 
                         'tax_id', 'vat_number']:
                if field in data:
                    setattr(address, field, data[field])
            address.save()
        else:
            # Create new address
            address = BillingAddress(
                user_id=user.id,
                company_name=data.get('company_name'),
                first_name=data['first_name'],
                last_name=data['last_name'],
                address_line_1=data['address_line_1'],
                address_line_2=data.get('address_line_2'),
                city=data['city'],
                state=data.get('state'),
                postal_code=data['postal_code'],
                country=data['country'],
                tax_id=data.get('tax_id'),
                vat_number=data.get('vat_number')
            )
            address.save()
        
        return jsonify({
            'message': 'Billing address saved successfully',
            'address': address.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Create billing address error: {e}")
        return jsonify({'error': 'Failed to save billing address'}), 500


@billing_bp.route('/payment-methods', methods=['GET'])
@login_required
def get_payment_methods():
    """Get user payment methods (Stripe integration)"""
    try:
        # TODO: Implement Stripe payment methods retrieval
        return jsonify({
            'payment_methods': [],
            'message': 'Payment methods integration coming soon'
        }), 200
        
    except Exception as e:
        logger.error(f"Get payment methods error: {e}")
        return jsonify({'error': 'Failed to get payment methods'}), 500


@billing_bp.route('/payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create Stripe payment intent"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        currency = data.get('currency', 'USD')
        
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400
        
        # TODO: Implement Stripe payment intent creation
        return jsonify({
            'client_secret': 'pi_test_client_secret',
            'message': 'Payment intent creation coming soon'
        }), 200
        
    except Exception as e:
        logger.error(f"Create payment intent error: {e}")
        return jsonify({'error': 'Failed to create payment intent'}), 500


# Admin endpoints
@billing_bp.route('/admin/invoices', methods=['GET'])
@admin_required
def admin_get_invoices():
    """Get all invoices (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        query = Invoice.query
        
        if status:
            query = query.filter_by(status=status)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        invoices = query.order_by(Invoice.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invoices.total,
                'pages': invoices.pages,
                'has_next': invoices.has_next,
                'has_prev': invoices.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Admin get invoices error: {e}")
        return jsonify({'error': 'Failed to get invoices'}), 500


@billing_bp.route('/admin/payments', methods=['GET'])
@admin_required
def admin_get_payments():
    """Get all payments (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        query = Payment.query
        
        if status:
            query = query.filter_by(status=status)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        payments = query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': payments.total,
                'pages': payments.pages,
                'has_next': payments.has_next,
                'has_prev': payments.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Admin get payments error: {e}")
        return jsonify({'error': 'Failed to get payments'}), 500
