import hmac
from hashlib import sha256, sha1
from datetime import datetime
import urllib, urllib2
from urlparse import urlparse
import base64
from flexpay.response import make_response
from flexpay.utils import make_enum, signature_quote, make_amount
from functools import wraps

__all__ = ["PaymentMethod", "CBUIStatus", "CBUIPipeline", "CurrencyCode", "SandboxAPI", "FlexPay"]

'''
Enumerated Values
You can convert string intro one of the enum's by using reverse_lookup.
For Example:
CC = PaymentMethod.reverse_lookup('CC')
'''

PaymentMethod = make_enum(str, 
                          CC = 'CC',   # Credit Card
                          ACH = 'ACH', # Bank Account Withdrawal
                          ABT = 'ABT') # Amazon Payments Balance Transfer
'''
Payment method's available on Amazon Flexible Payment Services.

    .. py:attribute:: PaymentMethod.CC

        Credit Card
        
    .. py:attribute:: PaymentMethod.ACH

        Bank Account Withdrawal
        
    .. py:attribute:: PaymentMethod.ABT

        Amazon Payments Balance Transfer
    
'''

CBUIStatus = make_enum(str,
                       SA='SA',
                       SB='SB',
                       SC='SC',
                       SE='SE',
                       A='A',
                       CE='CE',
                       PE='PE',
                       NP='NP')
'''
Status Codes Used By The Co-Branded User Interface Single Use Pipeline.

    See Also: http://docs.aws.amazon.com/AmazonFPS/latest/FPSMarketplaceGuide/SingleUsePipeline.html
    
    .. py:attribute:: CBUIStatus.SA

        Success status for the ABT payment method
        
    .. py:attribute:: CBUIStatus.SB

        Success status for the ACH (bank account) payment method.
        
    .. py:attribute:: CBUIStatus.SC

        Success status for the credit card payment method
        
    .. py:attribute:: CBUIStatus.SE

        System error
        
    .. py:attribute:: CBUIStatus.A

        Buyer abandoned the pipeline
        
    .. py:attribute:: CBUIStatus.CE

        Specifies a caller exception
        
    .. py:attribute:: CBUIStatus.PE

        Payment Method Mismatch Error: Specifies that the buyer does not have the payment method you requested
        
    .. py:attribute:: CBUIStatus.CE

        Any number of additional problems.
'''

CBUIPipeline = make_enum(str,
                         SingleUse='SingleUse',
                         MultiUse='MultiUse',
                         Recurring='Recurring',
                         Recipient='Recipient',
                         SetupPrepaid='SetupPrepaid',
                         SetupPostpaid='SetupPostpaid',
                         EditToken='EditToken')
"""
The Pipeline to use in the Co-Branded User Interface.

    .. py:attribute:: CBUIPipeline.SingleUse
    
        SingleUse is the one time payment pipeline.
        
    .. py:attribute:: CBUIPipeline.MultiUse
    
        MultiUse pipeline.
        
        See Also: 
            http://docs.aws.amazon.com/AmazonFPS/latest/FPSAdvancedGuide/MultipleUsePaymentTokens.html
        
    .. py:attribute:: CBUIPipeline.Recurring
    
        Payments of a fixed amount at regular intervals. For example weekly, monthly, etc.
        
        See Also: 
            http://docs.aws.amazon.com/AmazonFPS/latest/FPSAdvancedGuide/RecurringPaymentTokens.html
        
    .. py:attribute:: CBUIPipeline.Recipient
    
        You act as a 3rd part between a buyer and seller.
        
        See Also: 
            http://docs.aws.amazon.com/AmazonFPS/latest/FPSAdvancedGuide/RecipientToken.html
"""

CurrencyCode = make_enum(str,
                         USD='USD'
) # United States Dollars
"""
The currency code to use for all transaction. Note that Currently USD is the only supported currency for Amazon FPS. \
However Credit Cards might be a work around for international customers.

    .. py:attribute:: CurrencyCode.USD
    
        United State Dollars
"""

SandboxAPI = make_enum(str,
                API_URL='https://fps.sandbox.amazonaws.com/', 
                CBUI_URL='https://authorize.payments-sandbox.amazon.com/cobranded-ui/actions/start'
)
'''
SandboxAPI
URLS used by :py:class:`flexpay.payment.FlexPay` for the FPS sandbox environment.
    
    .. py:attribute:: SandboxAPI.API_URL
    
        Amazon FPS URL.
        
    .. py:attribute:: SandboxAPI.CBUI_URL
    
        Co-Branded User Interface URL.
        
When your ready for the production environment created your own with the correct production urls.

::

    ProductionAPI = make_enum(str,
        API_URL='...', 
        CBUI_URL='...'
    )
    
    # Then pass that ProductionAPI class to the FlexPay constructor.
    flex_pay = FlexPay(PUB_KEY, SECRET_KEY, api=ProductionAPI)
'''

def api_method(f):
    @wraps(f)
    def wrap(self, *args):
        params = f(self, *args)
        self.api_parameters(params)
        params['Signature'] = self.make_signature(params, self.api.API_URL)        
        return self.make_request(self.api.API_URL, params)
    return wrap

def cbui_api_method(f):
    @wraps(f)
    def wrap(self, *args):
        params = f(self, *args)
        self.cbui_api_parameters(params)
        params['signature'] = self.make_signature(params, self.api.CBUI_URL)
        return '{0}?{1}'.format(self.api.CBUI_URL, urllib.urlencode(params))
    return wrap

def find_signature_method(params, default):
    m = params.get('SignatureMethod', params.get('signatureMethod', default))
    if default == 'HmacSHA1':
        return sha1
    else:
        return sha256

class FlexPay:
    """
    FlexPay class.
    """
    
    def __init__(self, aws_public_key, aws_secret_key, api=SandboxAPI, currency_code=CurrencyCode.USD):
        '''
            :param aws_public_key: Your AWS public key.
            
            :param aws_secret_key: Your AWS sectey key. Used for signing requests.
            
            :param api: The API that you want to use. The default is :py:class:`flexpay.payment.SandboxAPI`.
            
            :param currency_code: The currency to use for transactions. Must be an instance of :py:class:`flexpay.payment.CurrencyCode`.
        '''
        self.pub_key = pub_key
        self.secret_key = secret_key
        self.currency_code = currency_code
        self.api = api
    
    def cbui_api_parameters(self, params):
        params['callerKey'] = self.pub_key
        params['signatureMethod'] = 'HmacSHA256'
        params['signatureVersion'] = 2
        
    def api_parameters(self, params):
        params['AWSAccessKeyId'] = self.pub_key
        params['SignatureMethod'] = 'HmacSHA256'
        params['SignatureVersion'] = 2
        params['Version'] = '2010-08-28'
        params['Timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        return params
    
    def make_signature(self, params, url):
        '''
        Generates a signature used by the 2010-08-28 version of the API.
        '''
        
        if 'Signature' in params:
            print 'deleting signature'
            del params['Signature']
        elif 'signature' in params:
            print 'deleting signature'
            del params['signature']
        
        # When returning from the cobranded ui url a different signature method may be present.
        # So we'll need to figure out which one to use in order to produce the correct signature.
        signature_method = find_signature_method(params, 'HmacSHA256')
        up = urlparse(url)
          
        qs = 'GET\n'
        qs += up.netloc + '\n'
        qs += up.path + '\n'
        
        qs += '&'.join(signature_quote(i[0]) + '=' + signature_quote(i[1]) for i in sorted(params.items()))
        sig = base64.b64encode(hmac.new(self.secret_key, qs, signature_method).digest())
        return sig
    
    def make_request(self, url, params):
        try:
            dest = '{0}?{1}'.format(url, urllib.urlencode(params))        
            response = urllib2.urlopen(dest)
            data = response.read()
            response.close()
            return make_response(data, params['Action'])
        except urllib2.HTTPError, httperror:
            data = httperror.read()
            httperror.close()
            raise RestAPIException(httperror.code, httperror.reason, data)
    
    @api_method
    def get_account_balance(self):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/GetAccountBalance.html
        '''
        params = {
            'Action': 'GetAccountBalance',
        }
        return params
    
    @api_method
    def verify_signature(self, url):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/VerifySignatureAPI.html
        '''        
        p = urlparse.urlparse(url)
        http_parameters = p.query
        url_end_point = '{0.scheme}://{0.netloc}{0.path}'.format(p)
        
        params = {
            'Action': 'VerifySignature',
            'UrlEndPoint': url_end_point,
            'HttpParameters': http_parameters,
        }
        return params
    
    @api_method
    def pay(self, 
            order_id,
            sender_id,
            amount,
            charge_to='Recipient'):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/Pay.html
        '''            
        params = {
            'Action': 'Pay',
            'ChargeFeeTo': charge_to,
            'TransactionAmount.Value': make_amount(amount),
            'TransactionAmount.CurrencyCode': self.currency_code,
            'SenderTokenId': sender_id,
            'CallerReference': order_id,
        }
        return params
    
    @api_method
    def refund(self, 
               order_id, 
               transaction_id, 
               amount = None, 
               refund_policy = 'MasterTxnOnly', 
               description = None):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/Refund.html
        '''
        params = {
            'Action': 'Pay',
            'CallerReference': order_id,
            'TransactionId': transaction_id,
            'MarketplaceRefundPolicy': refund_policy,
        }
        
        if amount != None:
            params['RefundAmount.Value'] = make_amount(amount)
            params['RefundAmount.CurrencyCode'] = self.currency_code
        
        if description != None:
            params['CallerDescription'] = description
        
        return params
    
    @api_method
    def reserve(self, 
                order_id,
                sender_id,
                amount,
                charge_to = 'Recipient',
                description = None):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/Reserve.html
        '''
        params = {
            'Action': 'Reserve',
            'ChargeFeeTo': charge_to,
            'TransactionAmount.Value': make_amount(amount),
            'TransactionAmount.CurrencyCode': self.currency_code,
            'SenderTokenId': sender_id,
            'CallerReference': order_id,
        }
        
        if description != None:
            params['CallerDescription'] = description
        return params
    
    @api_method
    def cancel(self, transaction_id):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/Cancel.html
        '''
        params = {
            'Action': 'Cancel',
            'TransactionId': transaction_id,
        }
        
        return params
        
    @api_method
    def cancel_token(self, token_id=None, reason_text=None):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/CancelToken.html
        '''
        params = {
            'Action': 'CancelToken',
            'TokenId': token_id,
        }
        
        if reason_text:
            params['ReasonText'] = reason_text
        
        return params
        
    @api_method
    def settle(self, transaction_id, amount=None):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/Settle.html
        '''
        params = {
            'Action': 'Settle',
            'ReserveTransactionId': transaction_id,
        }
        
        if amount != None:
            params['TransactionAmount.Value'] = make_amount(amount)
            params['TransactionAmount.CurrencyCode'] = self.currency_code
            
        return params
        
    @api_method
    def get_transaction_status(self, transaction_id):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/GetTransactionStatus.html
        '''
        params = {
            'Action': 'GetTransactionStatus',
            'TransactionId': transaction_id,
        }
        return params
        
    @api_method
    def get_token_by_caller(self, order_id=None, token_id=None):
        '''
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSAPIReference/GetTokensByCaller.html
        '''
        params = {
            'Action': 'GetTokenByCaller',
        }
        
        if order_id is not None:
            params['CallerReference'] = order_id
        
        if token_id is not None:
            params['TokenId'] = token_id
        
        return params
       
    @cbui_api_method
    def get_cbui_url(self, 
                     order_id,                        
                     return_url,
                     amount,
                     reason_text = None,
                     pipeline = CBUIPipeline.SingleUse,
                     paymentMethod = [ PaymentMethod.ABT, PaymentMethod.ACH, PaymentMethod.CC ]):
        
        """
        Generates a url for the Co-Branded User Interface pipeline.
        
        
        :param order_id: The id created by you that describes identifies the order.
            
        :param return_url: The URL that the sender will be redirected to once payment is complete. The query parameters will contain information about the status of the transaction.
            
        :param amount: The amount that the transaction is for. When using the SandboxAPI amounts where the decimal is between .60 and .89 can be used to simulate various error conditions.
            
        :param reason_text: Reason for the payment request. Will be shown to the sender on the CBUI checkout page.
            
        :param pipline: The CBUI Pipeline to use. The default is :py:obj:`flexpay.payment.CBUIPipeline.SingleUse`
            
        :param paymentMethod: A list of payment methods from the :py:class:`flexpay.payment.PaymentMethod` class.
        
        :Returns: 
            URL to the Amazon Co-Branded User Interface.
        
        http://docs.aws.amazon.com/AmazonFPS/latest/FPSBasicGuide/SingleUsePipeline.html
        """
        
        if not isinstance(pipeline, CBUIPipeline):
            raise TypeError('Argument pipeline should be an instance of CBUIPipeline.')
        
        # paymentMethod should be a list.
        if not isinstance(paymentMethod, list):
            paymentMethod = [ paymentMethod ]
        
        # Each element of the list should be an instance of PaymentMethod
        for pm in paymentMethod:
            if not isinstance(pm, PaymentMethod):
                raise TypeError('Argument paymentMethod should be a list of PaymentMethod instances.')
        
        params = {
            'callerReference': order_id,
            'currencyCode': self.currency_code,
            'paymentMethod': ','.join(paymentMethod),
            'transactionAmount': make_amount(amount),
            'pipelineName': pipeline,
            'returnURL': return_url,
        }
        
        if reason_text is not None:
            params['paymentReason'] = reason_text
        
        return params
