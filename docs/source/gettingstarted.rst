Getting Started
***************

About
=====

FlexPay is a wrapper for `Amazon's Flexible Payment Services <http://aws.amazon.com/fps/>`_.

Getting Your API Keys
=====================

Before you can use the sandbox you'll need to create an Amazon AWS account, sign up for FPS and obtain your API Key and Secret Key.

You do not have to attach a bank account to your profile in order to use the Sandbox.

Installation
============

Install from pip::

    $ pip install flexpay

Install from GitHub::

    $ git clone git://github.com/russelljk/flexpay.git
    $ cd flexpay
    $ python setup.py install
    
Interacting With FPS
====================

First create a new :py:class:`flexpay.payment.FlexPay` instance and make sure to pass both your **AWS Public Key** and your **AWS Secret Key** to the constructor.

By default all queries are done using the **FPS** sandbox.

::

    from flexpay import FlexPay, RestAPIException
    
    AWS_PUBLIC_KEY = 'My Public Key'
    AWS_SECRET_KEY = 'My Secret Key'
    
    flex_pay = FlexPay(AWS_PUBLIC_KEY, AWS_SECRET_KEY)

All API methods return a Response when successful::
   
    try:
        resp = flex_pay.get_account_balance()
        print( resp.AccountBalance.TotalBalance.Value )
    catch RestAPIException, rest_err:
        print rest_err

All dollar amounts returned are returned as strings. If you want a numerical value you can use the decimal class.

::

    from decimal import Decimal
    amount = Decimal( resp.AccountBalance.TotalBalance.Value )
    
Likewise any :py:class:`decimal.Decimal` or other floating point and currency classes will be converted to strings before being used in a query. The conversion method is in ``flexpay.utils.make_amount`` and simply amounts to creating a new string using the value in question.

You can also retreive the original response's **XML**::

    xml_body = resp.ResponseText
    print xml_body
