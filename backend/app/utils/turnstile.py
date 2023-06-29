import http.client
import json
import time
import uuid

class Turnstile:
    retry_errors = ["internal-error"]

    def __init__(self, sitekey, secret):
        self.sitekey = sitekey
        self.secret = secret

    def validate_response(self, response) -> bool:
        """
        Validates a Turnstile response using the siteverify endpoint.
        Returns True if the response is valid, False otherwise.
        """
        idemp_key = str(uuid.uuid4())
        conn = http.client.HTTPSConnection('challenges.cloudflare.com')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {
            'secret': self.secret,
            'response': response,
            'sitekey': self.sitekey,
            'idempotency_key': idemp_key
        }
        conn.request('POST', '/turnstile/v0/siteverify', body=json.dumps(data), headers=headers)
        retry = 0
        while retry < 3:
            response = conn.getresponse()
            if response.status == 200:
                break
            
            elif response.status == 443:
                error_codes = json.loads(response.read()).get('error-codes')
                if 'missing-input-secret' in error_codes:
                    raise ValueError('The secret parameter was not passed.')
                elif 'invalid-input-secret' in error_codes:
                    raise ValueError('The secret parameter was invalid or did not exist.')
                elif 'missing-input-response' in error_codes:
                    raise ValueError('The response parameter was not passed.')
                elif 'invalid-input-response' in error_codes:
                    raise ValueError('The response parameter is invalid or has expired.')
                elif 'invalid-widget-id' in error_codes:
                    raise ValueError('The widget ID extracted from the parsed site secret key was invalid or did not exist.')
                elif 'invalid-parsed-secret' in error_codes:
                    raise ValueError('The secret extracted from the parsed site secret key was invalid.')
                elif 'bad-request' in error_codes:
                    raise ValueError('The request was rejected because it was malformed.')
                elif 'timeout-or-duplicate' in error_codes:
                    raise ValueError('The response parameter has already been validated before.')
                return False
            
            if response.status == 429:
                retry += 1
                time.sleep(5)
                continue
            
            result = json.loads(response.read())
            if result.get('success') is True:
                return True
        return False
