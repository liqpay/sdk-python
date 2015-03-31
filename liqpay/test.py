# coding=utf-8
import unittest
from liqpay import LiqPay, ParamValidationError


class TestLiqPaySimple(unittest.TestCase):

    def setUp(self):
        self.liqpay = LiqPay('', '')
        self.maxDiff = None

    def test_api(self):
        self.assertTrue(self.liqpay.api("payment/status", {"payment_id": "3940"}))

    def test_gen_form(self):
        expected_form_out = (
            u'<form method="post" action="https://www.liqpay.com/api/checkout/" accept-charset="utf-8">\n'
            u'\t<input type="hidden" name="data" value="eyJwdWJsaWNfa2V5IjogIiIsICJkZXNjcmlwdGlvbiI6ICJcdTA0NDJcdTA0MzVcdTA0NDFcdTA0NDIiLCAibGFuZ3VhZ2UiOiAicnUiLCAic2FuZGJveCI6IDAsICJjdXJyZW5jeSI6ICJVQUgiLCAiYW1vdW50IjogIjM5NDAiLCAidGVzdCI6ICJjY2NjIn0="/>\n'
            u'\t<input type="hidden" name="signature" value="Zdm/xbS30v9ZTNXrLXeW9QFVxHQ="/>\n'
            u'    <input type="image" src="//static.liqpay.com/buttons/p1ru.radius.png" name="btn_text" />\n'
            u'</form>'
        )
        # test unicode issue with ru symbols
        params = {
            "amount": "3940",
            "currency": "UAH",
            "description": "тест",
            "test": "cccc"
        }
        self.assertEqual(self.liqpay.cnb_form(params), expected_form_out)

        # ru symbols in unicode
        params.update(description=u'тест')
        self.assertEqual(self.liqpay.cnb_form(params), expected_form_out)

        # test gen_form without required param
        del params['amount']
        self.assertRaises(ParamValidationError, self.liqpay.cnb_form, params)

if __name__ == '__main__':
    unittest.main()
