# sensor.authenticated

A platform which allows you to get information sucessfull logins to Home Assistant.

To get started put `/custom_components/sensor/authenticated.py` here:  
`<config directory>/custom_components/sensor/authenticated.py`  

**Example configuration.yaml:**

```yaml
sensor:
  - platform: authenticated
```

**Configuration variables:**

| key | required | default | description
| --- | --- | --- | ---
| **platform** | yes | | The sensor platform name.
| **enable_notification** | no | `true` | Turn on/off `persistant_notifications` when a new IP is detected, can be `true`/`false`.
| **exclude** | no | | A list of IP adresses you want to exclude.

**Sample overview:**\
![Sample overview](/img/overview.png)

If a new IP is detected, it will be added to a `.ip_authenticated.yaml` file in your configdir, with this information:

```yaml
8.8.8.8:
  city: Mountain View
  country: US
  hostname: google-public-dns-a.google.com
  last_authenticated: '2018-07-26 09:27:01'
  previous_authenticated_time: '2018-07-26 09:27:01'
  region: california
```

If not disabled, you will also be presented with a `persistant_notification` about the event:\
![notification](/img/persistant_notification.png)

## Debug logging

In your `configuration.yaml`

```yaml
logger:
  default: warn
  logs:
    custom_components.sensor.authenticated: debug
```
