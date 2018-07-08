# sensor.authenticated
  
[![Version](https://img.shields.io/badge/version-0.0.2-green.svg?style=for-the-badge)](#) [![mantained](https://img.shields.io/maintenance/yes/2018.svg?style=for-the-badge)](#) [![maintainer](https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge)](#)\
A platform which allows you to get information sucessfull logins to Home Assistant.
  
To get started put `/custom_components/sensor/authenticated.py` here:  
`<config directory>/custom_components/sensor/authenticated.py`  
  
**Example configuration.yaml:**

```yaml
sensor:
  platform: authenticated
```

**Configuration variables:**

key | description  
:--- | :---  
**platform (Required)** | The sensor platform name.  
  
**Sample overview:**\
![Sample overview](/img/overview.png)

If a new IP is detected, it will be added to a `.ip_authenticated.yaml` file in your configdir, with this information:\
![fileexample](/img/yamlfile.png)

You will also be presented with a `persistant_notification` about the event:\
![notification](/img/persistant_notification.png)