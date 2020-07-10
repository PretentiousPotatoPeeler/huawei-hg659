import sys, hashlib, base64, re, json
import logging

from requests import session
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

class Connector:
    host = None
    user = None
    pass_hash = None
    
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.pass_hash = hashlib.sha256(password.encode()).hexdigest()
        self.pass_hash = base64.b64encode(self.pass_hash.encode()).decode()

    def _connect(self):
        s = session()
        ## CSRF ##
        try:
            r = s.get('http://{0}'.format(self.host))
            html = BeautifulSoup(r.text, 'html.parser')
            data = {
                'csrf_param': html.find('meta', {'name':'csrf_param'}).get('content'),
                'csrf_token': html.find('meta', {'name':'csrf_token'}).get('content'),
            }
        except Exception as e:
            _LOGGER.error('Failed to get CSRF: {0}'.format(e))
            return None

        ## LOGIN ##
        try:
            pass_hash_csrf = self.user + self.pass_hash + data['csrf_param'] + data['csrf_token']
            pass_hash_csrf = hashlib.sha256(pass_hash_csrf.encode()).hexdigest()
            data = {'csrf':{'csrf_param':data['csrf_param'],'csrf_token':data['csrf_token']}, 'data':{'UserName':self.user,'Password':pass_hash_csrf}}
            r = s.post('http://{0}/api/system/user_login'.format(self.host), 
                data=json.dumps(data))
            data = json.loads(re.search('({.*?})', r.text).group(1))
            return (data, s)
        except Exception as e:
            _LOGGER.error('Failed to login: {0}'.format(e))
            return None
    
    def _disconnect(self, data, s):
        try:
            data = {'csrf':{'csrf_param':data['csrf_param'],'csrf_token':data['csrf_token']}}
            r = s.post('http://{0}/api/system/user_logout'.format(self.host), data=json.dumps(data))
        except Exception as e:
            _LOGGER.error('Failed to logout: {0}'.format(e))
    
    def getLanDevices(self):
        (data, s) = self._connect()
        try:
            r = s.get('http://{0}/api/system/HostInfo'.format(self.host))
            if r.status_code != 200:
                return []
            resp = json.loads(r.text[12:-2])
            props = []
            for item in resp:
                props.append(
                    {
                        'hostname': item['HostName'], 
                        'ip': item['IPAddress'], 
                        'mac': item['MACAddress'],
                        'active': item['Active']
                    })
            return props
        except Exception as e:
            _LOGGER.error('Failed to get devices: {0}'.format(e))
            return []
        finally:
            self._disconnect(data, s)
