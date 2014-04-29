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
            u'<form method="post" action="https://www.liqpay.com/api/pay/" accept-charset="utf-8">\n'
            u'\t<input type="hidden" name="public_key" value=""/>\n'
            u'\t<input type="hidden" name="description" value="\u0442\u0435\u0441\u0442"/>\n'
            u'\t<input type="hidden" name="language" value="ru"/>\n'
            u'\t<input type="hidden" name="sandbox" value="0"/>\n'
            u'\t<input type="hidden" name="currency" value="UAH"/>\n'
            u'\t<input type="hidden" name="amount" value="3940"/>\n'
            u'\t<input type="hidden" name="signature" value="jkwtxOAipwST6+xFKfleY/4ZES0="/>\n'
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
        self.assertEqual(self.liqpay.get_form(params), expected_form_out)

        # ru symbols in unicode
        params.update(description=u'тест')
        self.assertEqual(self.liqpay.get_form(params), expected_form_out)

        # test gen_form without required param
        del params['amount']
        self.assertRaises(ParamValidationError, self.liqpay.get_form, params)

if __name__ == '__main__':
    unittest.main()
