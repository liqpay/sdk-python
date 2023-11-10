import unittest
import base64
import hashlib
import json
from liqpay3 import LiqPay, ParamValidationError

class TestLiqPay(unittest.TestCase):

    def setUp(self):
        self.public_key = "your_public_key"
        self.private_key = "your_private_key"
        self.liqpay = LiqPay(self.public_key, self.private_key)


    def test_valid_params(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order',
            'language': 'en'
        }
        try:
            form = self.liqpay.cnb_form(params)
            self.assertIn('<form', form)
        except ParamValidationError:
            self.fail("cnb_form() raised ParamValidationError unexpectedly!")

    def test_unsupported_language_defaults_to_ukrainian(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order',
            'language': 'zz'
        }
        try:
            form = self.liqpay.cnb_form(params)
            self.assertIn('<form', form)
            self.assertIn("Сплатити", form)
        except ParamValidationError:
            self.fail("cnb_form() raised ParamValidationError unexpectedly!")

    def test_empty_version(self):
        params = {
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_valid_number_version(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        try:
            form = self.liqpay.cnb_form(params)
            self.assertIn('<form', form)
        except ParamValidationError:
            self.fail("cnb_form() raised ParamValidationError unexpectedly!")

    def test_valid_string_version(self):
        params = {
            'version': '3',
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        try:
            form = self.liqpay.cnb_form(params)
            self.assertIn('<form', form)
        except ParamValidationError:
            self.fail("cnb_form() raised ParamValidationError unexpectedly!")

    def test_invalid_currency(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'ABC',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_missing_amount(self):
        params = {
            'version': 3,
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_missing_currency(self):
        params = {
            'version': 3,
            'amount': '10',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_missing_action(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'order_id': '123456',
            'description': 'Test Order'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_missing_description(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456'
        }
        with self.assertRaises(ParamValidationError):
            self.liqpay.cnb_form(params)

    def test_cnb_form_generation(self):
        self.maxDiff = None
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order',
            'language': 'en',
            'public_key': 'your_public_key'
        }
        expected_signature = "x4uWEaw2f35T0IoiVfECyKsbIeY="
        expected_data_placeholder = self.encode_params_to_data(params)
        expected_form = """
        <form method="POST" action="https://www.liqpay.ua/api/3/checkout/" accept-charset="utf-8">
            <input type="hidden" name="data" value="{encoded_data}" />
            <input type="hidden" name="signature" value="{signature}" />
            <script type="text/javascript" src="https://static.liqpay.ua/libjs/sdk_button.js"></script>
            <sdk-button label="Pay" background="#77CC5D" onClick="submit()"></sdk-button>
        </form>
        """.format(encoded_data=expected_data_placeholder, signature=expected_signature).strip()

        generated_form = self.liqpay.cnb_form(params).strip()

        # Порівняти всі частини форми окрім значення data
        self.assertEqual(generated_form.replace(self.liqpay.data_to_sign(params), expected_data_placeholder),
                         expected_form)

        # Порівняти значення data окремо
        self.assertIn(self.liqpay.data_to_sign(params), generated_form)

    def test_decode_data_without_signature(self):
        data = {
            "order_id": "123456",
            "status": "success",
            "amount": "10.00"
        }
        encoded_data = base64.b64encode(json.dumps(data, sort_keys=True).encode("utf-8")).decode("utf-8")
        decoded_data = self.liqpay.decode_data_from_str(encoded_data)
        self.assertEqual(decoded_data, data)


    def test_decode_data_with_valid_signature(self):
        self.maxDiff = None
        expected_data = {
            'amount': '10.00',
            'order_id': '123456',
            'status': 'success'
        }
        encoded_data = self.encode_params_to_data(expected_data)
        # signature = "q9O87s+HTm4Ij+9z2Wtv6F7rzE8="
        signature = "mImHiMlo8z80jSh7+tWOz0enjIk="
        decoded_data = self.liqpay.decode_data_from_str(encoded_data, signature)

        self.assertEqual(decoded_data, expected_data)

    def test_decode_data_with_invalid_signature(self):
        encoded_data = "eyJhbW91bnQiOiAiMTAuMDAiLCAib3JkZXJfaWQiOiAiMTIzNDU2IiwgInN0YXR1cyI6ICJzdWNjZXNzIn0="
        invalid_signature = "invalid_signature"
        with self.assertRaises(ParamValidationError):
            self.liqpay.decode_data_from_str(encoded_data, invalid_signature)

    def test_signature_generation(self):
        params = {
            'version': 3,
            'amount': '10',
            'currency': 'USD',
            'action': 'pay',
            'order_id': '123456',
            'description': 'Test Order',
            'language': 'en',
            'public_key': self.public_key
        }
        expected_signature = "x4uWEaw2f35T0IoiVfECyKsbIeY="
        data, generated_signature = self.liqpay.get_data_end_signature("cnb_form", params)
        self.assertEqual(generated_signature, expected_signature)

    def encode_params_to_data(self, params):
        json_str = json.dumps(params, sort_keys=True)
        bytes_data = json_str.encode('utf-8')
        return base64.b64encode(bytes_data).decode("ascii")

if __name__ == '__main__':
    unittest.main()
