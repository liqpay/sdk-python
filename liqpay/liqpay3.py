"""
LiqPay Python SDK
~~~~~~~~~~~~~~~~~
supports python 3 version
requires requests module
"""

__title__ = 'LiqPay Python SDK'
__version__ = '1.0'

import base64
from copy import deepcopy
import hashlib
import json
from urllib.parse import urljoin

import requests




class ParamValidationError(Exception):
    pass


class LiqPay(object):
    FORM_TEMPLATE = u'''\
<form method="post" action="{action}" accept-charset="utf-8">
\t{param_inputs}
    <input type="image" src="//static.liqpay.com/buttons/p1{language}.radius.png" name="btn_text" />
</form>'''
    INPUT_TEMPLATE = u'<input type="hidden" name="{name}" value="{value}"/>'

    SUPPORTED_PARAMS = [
        'public_key', 'amount', 'currency', 'description', 'order_id',
        'result_url', 'server_url', 'type', 'signature', 'language', 'sandbox'
    ]

    def __init__(self, public_key, private_key, host='https://www.liqpay.com/api/'):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host

    def _make_signature(self, *args):
        joined_fields = ''.join(x for x in args)
        joined_fields = joined_fields.encode('utf-8')
        return base64.b64encode(hashlib.sha1(joined_fields).digest()).decode()

    def _prepare_params(self, params):
        params = {} if params is None else deepcopy(params)
        params.update(public_key=self._public_key)
        return params

    def api(self, url, params=None):
        params = self._prepare_params(params)

        json_encoded_params = json.dumps(params)
        private_key = self._private_key
        signature = self._make_signature(private_key, json_encoded_params, private_key)

        request_url = urljoin(self._host, url)
        request_data = {'data': json_encoded_params, 'signature': signature}
        response = requests.post(request_url, data=request_data, verify=False)
        return json.loads(response.content.decode('utf-8'))

    def cnb_form(self, params):
        params = self._prepare_params(params)
        params_validator = (
            ('amount', lambda x: x is not None and float(x) > 0),
            ('description', lambda x: x is not None)
        )
        for key, validator in params_validator:
            if validator(params.get(key)):
                continue

            raise ParamValidationError('Invalid param: "%s"' % key)

        # spike to set correct values for language, currency and sandbox params
        language = params.get('language', 'ru')
        currency = params['currency']
        params.update(
            language=language,
            currency=currency if currency != 'RUR' else 'RUB',
            sandbox=int(bool(params.get('sandbox')))
        )
        params_templ = {'data': base64.b64encode(json.dumps(params).encode()).decode()}
        params_templ['signature'] = self._make_signature(self._private_key, params_templ['data'], self._private_key)
        form_action_url = urljoin(self._host, '3/checkout/')
        format_input = lambda k, v: self.INPUT_TEMPLATE.format(name=k, value=v)
        inputs = [format_input(k, v) for k, v in params_templ.items()]
        return self.FORM_TEMPLATE.format(
            action=form_action_url,
            language=language,
            param_inputs=u'\n\t'.join(inputs)
        )

    def cnb_signature(self, params):
        params = self._prepare_params(params)
        print(base64.b64encode(json.dumps(params)))
        return self._make_signature(self._private_key, base64.b64encode(json.dumps(params)), self._private_key)

    def str_to_sign(self, str):
        return base64.b64encode(hashlib.sha1(str).digest())
