"""
This module provides simple APIs that accept Oscar objects as parameters. It
decomposes these into dictionaries of data that are passed to the fine-grained
APIs of the gateway module.
"""
from oscar.apps.payment import exceptions as oscar_exceptions

from . import gateway, exceptions


def authenticate(amount, bankcard, shipping_address=None, description=''):
    """
    Perform an AUTHENTICATE request and return the TX ID if successful.
    """
    # Decompose Oscar objects into a dict of data to pass to gateway
    params = {
        'amount': amount.incl_tax,
        'currency': amount.currency,
        'description': description,
        'bankcard_number': bankcard.number,
        'bankcard_cv2': bankcard.ccv,
        'bankcard_name': bankcard.name,
        'bankcard_expiry': bankcard.expiry_month('%m%y'),
    }
    if shipping_address:
        params.update({
            'delivery_surname': shipping_address.last_name,
            'delivery_first_names': shipping_address.first_name,
            'delivery_address1': shipping_address.line1,
            'delivery_address2': shipping_address.line2,
            'delivery_city': shipping_address.line4,
            'delivery_postcode': shipping_address.postcode,
            'delivery_country': shipping_address.country.code,
            'delivery_state': shipping_address.state,
            'delivery_phone': shipping_address.phone_number,
        })

    try:
        response = gateway.authenticate(**params)
    except exceptions.GatewayError as e:
        # Translate Sagepay gateway exceptions into Oscar checkout ones
        raise oscar_exceptions.PaymentError(e.message)

    # Check if the transaction was successful
    if not response.is_successful:
        raise oscar_exceptions.UnableToTakePayment(
            response.status_detail)

    return response.tx_id