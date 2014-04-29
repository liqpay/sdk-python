======================================
LiqPay python software development kit
======================================

--------------------------
Создание кнопки для оплаты
--------------------------

from liqpay import LiqPay

liqpay = LiqPay(public_key, private_key)
liqpay.get_form({
    "amount": "3940",
    "currency": "UAH",
    "description": "тест",
    "test": "cccc"
})

[Возможные параметры]

============  ============
 параметр     обязательный
============  ============
 amount	       Да
 currency	   Да
 description   Да
 order_id	   Нет
 result_url	   Нет
 server_url	   Нет
 type	       Нет
 language	   Нет
 order_id	   Нет
============  ============

------------------------
Проверка статуса платежа
------------------------

from liqpay import LiqPay

liqpay = LiqPay(public_key, private_key)
liqpay.api("payment/status", {"order_id": "order_id_123"})
