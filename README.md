# huawei-hg659

Scraper for Huawei HG659 Router to get the connected devices.

## Usage

```python
from huawei_hg659 import Connector
c = Connector('ip', 'user', 'pass')
c.getLanDevices()
# [{host: 'HOSTNAME', ip: 'IP', mac: 'MAC', active: True|False}]
```


## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
