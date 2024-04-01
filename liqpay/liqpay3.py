"""
LiqPay Python SDK
~~~~~~~~~~~~~~~~~
supports python 3 version
requires requests module
"""

__title__ = "LiqPay Python SDK"
__version__ = "1.1"

import base64
from copy import deepcopy
import hashlib
import json
from urllib.parse import urljoin

import requests


class ParamValidationError(Exception):
    pass


class LiqPay(object):
    _supportedCurrencies = ['EUR', 'USD', 'UAH']
    _supportedLangs = ['uk', 'en']
    _supportedActions = ['pay', 'hold', 'subscribe', 'paydonate']

    _button_translations = {
        'uk': 'Сплатити',
        'en': 'Pay'
    }

    _FORM_TEMPLATE = """
        <form method="POST" action="{action}" accept-charset="utf-8">
            <input type="hidden" name="data" value="{data}" />
            <input type="hidden" name="signature" value="{signature}" />
            <script type="text/javascript" src="https://static.liqpay.ua/libjs/sdk_button.js"></script>
            <sdk-button label="{label}" background="#77CC5D" onClick="submit()"></sdk-button>
        </form>
    """

    SUPPORTED_PARAMS = [
        "public_key", "amount", "currency", "description", "order_id",
        "result_url", "server_url", "type", "signature", "language",
        "version", "action"
    ]

    def __init__(self, public_key, private_key, host="https://www.liqpay.ua/api/"):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host

    def _make_signature(self, *args):
        joined_fields = "".join(x for x in args)
        joined_fields = joined_fields.encode("utf-8")
        return base64.b64encode(hashlib.sha1(joined_fields).digest()).decode("ascii")


    def _prepare_params(self, params):
        params = {} if params is None else deepcopy(params)
        params.update(public_key=self._public_key)
        return params

    def api(self, url, params=None):
        params = self._prepare_params(params)
        params_validator = (
                    ("version", lambda x: x is not None),
                    ("action", lambda x: x is not None),
                )
        for key, validator in params_validator:
             if validator(params.get(key)):
                continue
             raise ParamValidationError("Invalid param: '{}'".format(key))

        encoded_data, signature = self.get_data_end_signature('api', params)

        request_url = urljoin(self._host, url)
        request_data = {"data": encoded_data, "signature": signature}
        response = requests.post(request_url, data=request_data, verify=True)
        return json.loads(response.content.decode("utf-8"))

    def cnb_form(self, params):
        params = self._prepare_params(params)

        params_validator = (
            ("version", lambda x: x is not None),
            ("amount", lambda x: x is not None and float(x) > 0),
            ("currency", lambda x: x is not None and x in self._supportedCurrencies),
            ("action", lambda x: x is not None),
            ("description", lambda x: x is not None and isinstance(x, str))
        )
        for key, validator in params_validator:
            if validator(params.get(key)):
                continue

            raise ParamValidationError("Invalid param: '{}'".format(key))

        if 'language' in params:
            language = params['language'].lower()
            if language not in self._supportedLangs:
                params['language'] = 'uk'
                language = 'uk'
        else:
            language = 'uk'

        encoded_data, signature = self.get_data_end_signature('cnb_form', params)

        form_action_url = urljoin(self._host, "3/checkout/")
        return self._FORM_TEMPLATE.format(
            action=form_action_url,
            data=encoded_data,
            signature=signature,
            label=self._button_translations[language]
        )

    def get_data_end_signature(self, type, params):
        json_encoded_params = json.dumps(params, sort_keys=True)
        if type == "cnb_form":
            bytes_data = json_encoded_params.encode('utf-8')
            base64_encoded_params = base64.b64encode(bytes_data).decode('utf-8')
            signature = self._make_signature(self._private_key, base64_encoded_params, self._private_key)
            return base64_encoded_params, signature
        else:
            signature = self._make_signature(self._private_key, json_encoded_params, self._private_key)
        return json_encoded_params, signature

    def cnb_signature(self, params):
        params = self._prepare_params(params)

        data_to_sign = self.data_to_sign(params)
        return self._make_signature(self._private_key, data_to_sign, self._private_key)

    def cnb_data(self, params):
        params = self._prepare_params(params)
        return self.data_to_sign(params)

    def str_to_sign(self, str):
        return base64.b64encode(hashlib.sha1(str.encode("utf-8")).digest()).decode("ascii")

    def data_to_sign(self, params):
        json_encoded_params = json.dumps(params, sort_keys=True)
        bytes_data = json_encoded_params.encode('utf-8')
        return base64.b64encode(bytes_data).decode('utf-8')

    def decode_data_from_str(self, data, signature=None):
        """Decoding data that were encoded by base64.b64encode(str)

        Args:
            data: json string with api params and encoded by base64.b64encode(str).
            signature: signature received from LiqPay (optional).

        Returns:
            Dict

        Raises:
            ParamValidationError: If the signature is provided and is invalid.

        """
        if signature:
            expected_signature = self._make_signature(self._private_key, base64.b64decode(data).decode('utf-8'), self._private_key)
            if expected_signature != signature:
                raise ParamValidationError("Invalid signature")

        return json.loads(base64.b64decode(data).decode('utf-8'))

