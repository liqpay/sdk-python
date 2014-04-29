#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='liqpay-python',
    version='1.0',
    description='LiqPay Python SDK',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests']
)
