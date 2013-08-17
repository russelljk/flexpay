Working With FlexPay
********************

Typical Workflow
================

Generating The Co-Branded User Interface (CBUI) URL
---------------------------------------------------

When a customer checks out you'll want to generate the cobrandedui url. 

For this action you will use the method :py:meth:`flexpay.payment.FlexPay.get_cbui_url`::
    
    import decimal
        
    cbui_url = flex_pay.get_cbui_url(order.id, 
        reason, 
        order.amount,
        return_url
    )
    
The `return_url` should point to a be where the user will finish the transaction. While order_id, amount and reason should relate to the order being processed.

Then redirect the user so that he/she can pay using whatever redirect method your framework provides.

For example in Django::
    
    from django.shortcuts import redirect
    
    def checkout(request):
        if request.method == 'POST':
            ...
            return redirect(cbui_url)

Checking The Result From the CBUI
---------------------------------

Immediate Billing
-----------------

Bill When Shipped
-----------------

Error Recovery
==============

This will cover what to do when things go wrong. I recommend reading both the Amazon FPS Quick Start guide and going over the API documentation as well. Remember that you use cases may dictate different actions depending on you and your customers needs.

Always test for failure conditions when interacting with Amazon FPS.

User Never Returns
------------------

Sometimes the user will not return to your website after completing payment via the CBUI. If this happens you can still grab the result of that interaction.