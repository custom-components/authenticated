# sensor.authenticated

A platform which allows you to get information sucessfull logins to Home Assistant.
  
To get started put `/custom_components/sensor/authenticated.py` here:  
`<config directory>/custom_components/sensor/authenticated.py`  
  
**Example configuration.yaml:**

```yaml
sensor:
  platform: authenticated
  enable_notification: 'True'
```

**Configuration variables:**

key | description  
:--- | :---  
**platform (Required)** | The sensor platform name.
**enable_notification (Optional)** | Turn on/off `persistant_notifications` when a new IP is detected, can be `True`/`False` defaults to `True`.
  
**Sample overview:**\
![Sample overview](/img/overview.png)

If a new IP is detected, it will be added to a `.ip_authenticated.yaml` file in your configdir, with this information:\
![fileexample](/img/yamlfile.png)

If not disabled, you will also be presented with a `persistant_notification` about the event:\
![notification](/img/persistant_notification.png)