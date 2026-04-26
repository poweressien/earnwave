"""
EarnWave Paystack Integration
Handles airtime disbursement via Paystack API
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class PaystackService:
    BASE_URL = 'https://api.paystack.co'

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    def _post(self, endpoint, data):
        try:
            response = requests.post(
                f'{self.BASE_URL}{endpoint}',
                json=data,
                headers=self.headers,
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Paystack API error: {e}')
            return {'status': False, 'message': str(e)}

    def _get(self, endpoint):
        try:
            response = requests.get(
                f'{self.BASE_URL}{endpoint}',
                headers=self.headers,
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Paystack API error: {e}')
            return {'status': False, 'message': str(e)}

    def send_airtime(self, phone_number, amount_naira, network):
        """
        Send airtime directly via Paystack Airtime API.
        amount_naira: float (e.g. 100.0 for ₦100)
        network: MTN | Airtel | Glo | 9mobile
        """
        # Normalize phone to international format
        phone = self._normalize_phone(phone_number)

        # Paystack airtime provider codes
        provider_map = {
            'MTN': 'MTN',
            'Airtel': 'Airtel',
            'Glo': 'Glo',
            '9mobile': '9mobile',
        }

        data = {
            'currency': 'NGN',
            'amount': int(amount_naira * 100),  # Paystack uses kobo
            'phone': phone,
            'provider_slug': provider_map.get(network, network).lower(),
        }

        result = self._post('/charge', data)
        logger.info(f'Airtime send result: {result}')
        return result

    def verify_transaction(self, reference):
        """Verify a Paystack transaction by reference."""
        return self._get(f'/transaction/verify/{reference}')

    def get_balance(self):
        """Get your Paystack wallet balance."""
        return self._get('/balance')

    def initialize_payment(self, email, amount_naira, reference, callback_url):
        """Initialize a payment (for wallet top-ups)."""
        data = {
            'email': email,
            'amount': int(amount_naira * 100),
            'reference': reference,
            'callback_url': callback_url,
            'currency': 'NGN',
        }
        return self._post('/transaction/initialize', data)

    @staticmethod
    def _normalize_phone(phone):
        """Convert 0812... to +234812..."""
        phone = phone.strip().replace(' ', '').replace('-', '')
        if phone.startswith('0'):
            phone = '+234' + phone[1:]
        elif phone.startswith('234'):
            phone = '+' + phone
        elif not phone.startswith('+'):
            phone = '+234' + phone
        return phone

    def process_redemption(self, redemption):
        """
        Process an AirtimeRedemption record via Paystack.
        Updates redemption status and paystack_reference.
        """
        from django.utils import timezone
        import uuid

        reference = f'ew-{redemption.id}-{uuid.uuid4().hex[:8]}'
        result = self.send_airtime(
            phone_number=redemption.phone_number,
            amount_naira=float(redemption.airtime_amount),
            network=redemption.network,
        )

        if result.get('status'):
            redemption.status = 'completed'
            redemption.paystack_reference = reference
            redemption.processed_at = timezone.now()
            redemption.admin_note = f'Auto-processed via Paystack. Ref: {reference}'
        else:
            redemption.status = 'failed'
            redemption.admin_note = f'Paystack error: {result.get("message", "Unknown error")}'

        redemption.save()
        return result


# Singleton instance
paystack = PaystackService()
