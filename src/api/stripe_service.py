"""
stripe_service.py
Servicio para manejar todas las operaciones con Stripe
"""
import os
import stripe
from datetime import datetime, timezone
from flask import current_app

# Configurar Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

class StripeService:
    """Servicio para operaciones con Stripe"""
    
    @staticmethod
    def create_payment_intent(amount_cents, currency='usd', metadata=None, description="", customer_email=""):
        """
        Crea un PaymentIntent en Stripe
        
        Args:
            amount_cents (int): Monto en centavos
            currency (str): Moneda (ej: 'usd')
            metadata (dict): Metadatos adicionales
            description (str): Descripción del pago
            customer_email (str): Email del cliente
            
        Returns:
            dict: PaymentIntent creado
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                description=description[:300],  # Limitar longitud
                receipt_email=customer_email if customer_email else None,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )
            
            return {
                'success': True,
                'payment_intent': payment_intent,
                'client_secret': payment_intent.client_secret,
                'id': payment_intent.id
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ Error de Stripe al crear PaymentIntent: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'stripe_error'
            }
        except Exception as e:
            print(f"❌ Error inesperado al crear PaymentIntent: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error'
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Recupera un PaymentIntent de Stripe
        
        Args:
            payment_intent_id (str): ID del PaymentIntent
            
        Returns:
            dict: PaymentIntent recuperado o error
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'payment_intent': payment_intent,
                'status': payment_intent.status
            }
        except stripe.error.StripeError as e:
            print(f"❌ Error de Stripe al recuperar PaymentIntent: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_webhook_signature(payload, sig_header):
        """
        Verifica que un webhook venga realmente de Stripe
        
        Args:
            payload (str): Cuerpo de la solicitud
            sig_header (str): Encabezado 'Stripe-Signature'
            
        Returns:
            dict: Evento verificado o error
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, 
                sig_header, 
                STRIPE_WEBHOOK_SECRET
            )
            return {
                'success': True,
                'event': event,
                'type': event['type']
            }
        except ValueError as e:
            print(f"⚠️ Error en payload del webhook: {e}")
            return {
                'success': False,
                'error': 'Invalid payload',
                'details': str(e)
            }
        except stripe.error.SignatureVerificationError as e:
            print(f"⚠️ Firma inválida del webhook: {e}")
            return {
                'success': False,
                'error': 'Invalid signature',
                'details': str(e)
            }
    
    @staticmethod
    def create_metadata_for_purchase(purchase_id, user_id, course_id, course_title):
        """
        Crea metadata estándar para pagos de cursos
        
        Args:
            purchase_id (int): ID de la compra en tu DB
            user_id (int): ID del usuario
            course_id (int): ID del curso
            course_title (str): Título del curso
            
        Returns:
            dict: Metadata formateada para Stripe
        """
        return {
            'purchase_id': str(purchase_id),
            'user_id': str(user_id),
            'course_id': str(course_id),
            'course_title': course_title[:100],  # Limitar longitud
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def format_amount_for_stripe(amount):
        """
        Convierte un monto decimal a centavos para Stripe
        
        Args:
            amount (float): Monto en dólares (ej: 10.50)
            
        Returns:
            int: Monto en centavos (ej: 1050)
        """
        try:
            return int(float(amount) * 100)
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def get_stripe_config():
        """
        Obtiene configuración de Stripe para el frontend
        
        Returns:
            dict: Configuración segura para frontend
        """
        return {
            'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY', ''),
            'api_version': '2023-10-16',
            'currency': 'USD',
            'country': 'US'
        }


# Instancia global del servicio
stripe_service = StripeService()