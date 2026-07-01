# -*- coding: utf-8 -*-

import requests
import json


session = requests.session()


headers = {
    'Authorization': 'Bearer 7a2a3ff2-fa27-40f9-aafc-9b0195e870e2',
}

url = 'http://localhost:8069/api/catalogominsa.renipress.eess'

params = {'procedimiento_nombre__lge': 'vih',
          'pagination': 1000000,
          'page': 1,
          'only_fields': 'procedimiento_nombre'}
params = {}

res = session.get(url, data=json.dumps({}),
                  headers=headers,
                  params=params)

if res.status_code == 200:
    res = res.text and json.loads(res.text) or {}
    print res
else:
    print res.text
