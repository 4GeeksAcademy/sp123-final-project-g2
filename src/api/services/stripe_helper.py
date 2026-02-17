# services/stripe_helper.py
import os
import stripe
from datetime import datetime
# Ya no necesitamos importar current_app aquí para el inicio

class StripeHelper:
    """Helper para centralizar toda la lógica de Stripe"""
    
    def __init__(self):
        # Cargamos las llaves directamente del sistema operativo (.env)
        # Esto evita el error "Working outside of application context"
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        if self.api_key:
            stripe.api_key = self.api_key
        else:
            print("⚠️ Advertencia: STRIPE_SECRET_KEY no encontrada en el archivo .env")
    
    def format_amount_for_stripe(self, amount):
        """Convierte precio a centavos para Stripe"""
        return int(round(amount * 100))
    
    def create_metadata_for_purchase(self, purchase_id, user_id, course_id, course_title):
        """Crea metadata estándar para compras"""
        return {
            'purchase_id': str(purchase_id),
            'user_id': str(user_id),
            'course_id': str(course_id),
            'course_title': course_title,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_payment_intent(self, amount_cents, currency, metadata, description, customer_email=None):
        """
        Crea un PaymentIntent en Stripe
        Retorna: dict con success, id, client_secret o error
        """
        try:
            payment_intent_params = {
                'amount': amount_cents,
                'currency': currency,
                'metadata': metadata,
                'description': description
            }
            
            if customer_email:
                # Buscar o crear customer por email para mejor tracking
                customers = stripe.Customer.list(email=customer_email, limit=1)
                if customers.data:
                    payment_intent_params['customer'] = customers.data[0].id
                else:
                    customer = stripe.Customer.create(email=customer_email)
                    payment_intent_params['customer'] = customer.id
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            
            return {
                'success': True,
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': f"Error de Stripe: {str(e)}",
                'code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error inesperado: {str(e)}"
            }
    
    def get_stripe_config(self):
        """Retorna configuración pública de Stripe para el frontend"""
        return {
            'publishable_key': self.publishable_key,
            'currency': 'usd',
            'api_version': stripe.api_version
        }
    
    def validate_amount(self, amount_cents):
        """Valida que el monto sea aceptado por Stripe"""
        if amount_cents < 50:
            return False, "El monto mínimo es $0.50 USD"
        if amount_cents > 99999900:  # Límite de Stripe
            return False, "El monto excede el límite permitido"
        return True, None
    
    def confirm_payment_intent(self, payment_intent_id):
        """Confirma un PaymentIntent (útil para webhooks)"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'metadata': payment_intent.metadata
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

# Instancia global para usar en las rutas
# Ahora se inicializará correctamente al importar el módulo
stripe_helper = StripeHelper()