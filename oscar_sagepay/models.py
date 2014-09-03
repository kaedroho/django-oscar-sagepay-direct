import json

from django.db import models


class RequestResponse(models.Model):
    # Request fields
    protocol = models.CharField(max_length=12, blank=True)
    tx_type = models.CharField(max_length=64, blank=True)
    vendor = models.CharField(max_length=128, blank=True)

    # We allow this unique field to be null so a blank instance can be created
    # to provide a PK that forms part of the vendor tx code.
    vendor_tx_code = models.CharField(max_length=128, unique=True, null=True,
                                      blank=True)

    amount = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True)
    description = models.CharField(max_length=512, blank=True)

    raw_request_json = models.TextField(blank=True)

    # Response fields
    status = models.CharField(max_length=128, blank=True)
    status_detail = models.TextField(blank=True)
    tx_id = models.CharField(max_length=128, blank=True)
    tx_auth_num = models.CharField(max_length=32, blank=True)
    security_key = models.CharField(max_length=128, blank=True)
    raw_response = models.TextField(blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.vendor_tx_code

    @property
    def raw_request(self):
        return json.loads(self.raw_request_json)

    def record_request(self, params):
        """
        Update fields based on request params
        """
        self.protocol = params['VPSProtocol']
        self.tx_type = params['TxType']
        self.vendor = params['Vendor']
        self.vendor_tx_code = params['VendorTxCode']
        self.amount = params['Amount']
        self.currency = params.get('Currency', '')
        self.description = params.get('Description', '')

        # Remove cardholder data so we can keep our PCI compliance level down
        sensitive_fields = (
            'CardHolder', 'CardNumber', 'ExpiryDate', 'CV2', 'CardType')
        safe_params = params.copy()
        for key in sensitive_fields:
            if key in safe_params:
                safe_params[key] = '<removed>'
        self.raw_request_json = json.dumps(safe_params)

    def record_response(self, response):
        """
        Update fields based on Response instance
        """
        self.status = response.status
        self.status_detail = response.status_detail
        self.tx_id = response.tx_id
        self.tx_auth_num = response.tx_auth_num
        self.security_key = response.security_key
        self.raw_response = response.raw
