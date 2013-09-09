FlexPay 0.1
***********

Copyright 2013 Russell Kyle russell.j.kyle@gmail.com

Note
====

FlexPay is still in early development.

Overview
========

FlexPay is a wrapper to Amazon's `Flexible Payments Service <http://aws.amazon.com/fps/>`_ aka (**FPS**). Remember to always use the Amazon FPS Sandbox when developing and testing.

License
-------

FlexPay is release under the zlib License and can be used for commercial, education and personal projects.

Links
-----

* **FlexPay GitHub Repository** - `<https://github.com/russelljk/flexpay/>`_
* **FlexPay** - *Coming Soon*...
* **Amazon Flexible Payments Service** - `<http://aws.amazon.com/fps/>`_
* **FPS Quick Start Guide** - `<http://docs.aws.amazon.com/AmazonFPS/latest/FPSBasicGuide/intro.html>`_

Quick Start
===========

Installation
------------

Currently **FlexPay** is not listed on **pip** so you can install directly from **GitHub** or download
and run ``setup.py`` yourself.

Install via **pip**::

    $ pip install flexpay

Install directly from **GitHub**::

    $ git clone git://github.com/russelljk/flexpay.git
    $ cd flexpay
    $ python setup.py install

Getting Started
---------------

Import the ``FlexPay`` class and create a new instance. Make sure to pass both your public and secret key for AWS.

::

    from flexpay import *
    
    flex_pay = FlexPay('AMAZON_PUBLIC_KEY', 'AMAZON_SECRET_KEY')

When a user checkouts you'll want to generate a cobranded-ui url and redirect to it. The ``return_url`` should point to a be where the user will finish the transaction.

::
    
    import decimal
    
    order = Order('0.50')
    
    cbui_url = flex_pay.get_cbui_url(order.id, 
        reason, 
        order.amount,
        return_url
    )
    
    # Use whatever method your CMS/Framework provides for url redirection.
    redirect(cbui_url)

Later on when the user returns to the site after completing checkout you use ``FlexPay.pay`` to charge the user immediately. 

Or you can use ``FlexPay.reserve`` and then at a later date ``FlexPay.settle``. You would want to use reserve if, for example, you haven't shipped the product yet.

::
    
    resp = flex_pay.pay(order.id,
        order.sender_id,
        order.amount
    )

For more examples and documentation please visit the `GitHub page for FlexPay <https://github.com/russelljk/flexpay/>`_.
