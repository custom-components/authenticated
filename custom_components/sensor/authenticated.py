"""
A platform which allows you to get information about sucessfull logins to Home Assistant.
For more details about this component, please refer to the documentation at
https://github.com/custom-components/sensor.authenticated
"""
import logging
import socket
from datetime import timedelta
from pathlib import Path
import requests
import voluptuous as vol
import yaml
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

__version__ = '0.0.6'

_LOGGER = logging.getLogger(__name__)

CONF_NOTIFY = 'enable_notification'
CONF_EXCLUDE = 'exclude'

ATTR_HOSTNAME = 'hostname'
ATTR_COUNTRY = 'country'
ATTR_REGION = 'region'
ATTR_CITY = 'city'
ATTR_NEW_IP = 'new_ip'
ATTR_LAST_AUTHENTICATE_TIME = 'last_authenticated_time'
ATTR_PREVIOUS_AUTHENTICATE_TIME = 'previous_authenticated_time'

SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_NAME = 'authenticated'

LOGFILE = 'home-assistant.log'
OUTFILE = '.ip_authenticated.yaml'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NOTIFY, default='True'): cv.string,
    vol.Optional(CONF_EXCLUDE, default='None'):
        vol.All(cv.ensure_list, [cv.string]),
    })

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Create the sensor"""
    notify = config.get(CONF_NOTIFY)
    exclude = config.get(CONF_EXCLUDE)
    logs = {'homeassistant.components.http.view': 'info'}
    _LOGGER.debug('Making sure the logger is correct set.')
    hass.services.call('logger', 'set_level', logs)
    log = str(hass.config.path(LOGFILE))
    out = str(hass.config.path(OUTFILE))
    add_devices([Authenticated(hass, notify, log, out, exclude)])

class Authenticated(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, notify, log, out, exclude):
        """Initialize the sensor."""
        _LOGGER.info('version %s is starting, if you have ANY issues with this, please report them here: https://github.com/custom-components/%s', __version__, __name__.split('.')[1] + '.' + __name__.split('.')[2])
        self._state = None
        self._hostname = None
        self._country = None
        self._region = None
        self._city = None
        self._new_ip = 'false'
        self._last_authenticated_time = None
        self._previous_authenticated_time = None
        self._exclude = exclude
        self._notify = notify
        self._log = log
        self._out = out
        self.hass = hass
        self.update()

    def first_ip(self, ip_address, access_time, hostname):
        """If the IP is the first"""
        _LOGGER.debug('First IP, creating file...')
        with open(self._out, 'a') as the_file:
            the_file.write(ip_address + ':')
        self.new_ip(ip_address, access_time, hostname)
        the_file.close()

    def new_ip(self, ip_address, access_time, hostname):
        """If the IP is new"""
        _LOGGER.debug('Found new IP %s', ip_address)
        fetchurl = 'https://ipvigilante.com/json/' + ip_address
        try:
            geo = requests.get(fetchurl, timeout=5).json()
        except:
            geo = 'none'
        else:
            geo = geo
        if geo['status'] == 'error':
            _LOGGER.debug('The IP is reserved, no GEO info available...')
            geo_country = 'none'
            geo_region = 'none'
            geo_city = 'none'
        else:
            geo_country = geo['data']['country_name']
            geo_region = geo['data']['subdivision_1_name']
            geo_city = geo['data']['city_name']
        self.write_file(ip_address, access_time, hostname, geo_country, geo_region, geo_city)
        self._new_ip = 'true'
        if self._notify == 'True':
            self.hass.components.persistent_notification.create('{}'.format(ip_address + ' (' + geo_country + ', ' + geo_region + ', ' + geo_city + ')'), 'New successful login from')
        else:
            _LOGGER.debug('persistent_notifications is disabled in config, enable_notification=%s', self._notify)

    def update_ip(self, ip_address, access_time, hostname):
        """If we know this IP"""
        _LOGGER.debug('Found known IP %s, updating timestamps.', ip_address)
        with open(self._out) as f:
            doc = yaml.load(f)
        f.close()

        doc[ip_address]['previous_authenticated_time'] = doc[ip_address]['last_authenticated']
        doc[ip_address]['last_authenticated'] = access_time
        doc[ip_address]['hostname'] = hostname

        self._new_ip = 'false'

        with open(self._out, 'w') as f:
            yaml.dump(doc, f, default_flow_style=False)
        f.close()

    def write_file(self, ip_address, access_time, hostname, country='none', region='none', city='none'):
        """Writes info to out control file"""
        with open(self._out) as f:
            doc = yaml.load(f)
        f.close()

        doc[ip_address] = dict(
            hostname=hostname,
            last_authenticated=access_time,
            previous_authenticated_time='none',
            country=country,
            region=region,
            city=city
        )

        with open(self._out, 'w') as f:
            yaml.dump(doc, f, default_flow_style=False)
        f.close()

    def update(self):
        """Method to update sensor value"""
        _LOGGER.debug('Searching log file for IP adresses.')
        get_ip = []
        with open(self._log) as f:
            for line in f.readlines():
                if '(auth: True)' in line:
                    get_ip.append(line)
        if not get_ip:
            _LOGGER.debug('No IP Addresses found in the log...')
            self._state = None
        else:
            for line in get_ip:
                ip_address = line.split(' ')[8]
                _LOGGER.debug('Started prosessing for %s', ip_address)
                if ip_address not in self._exclude:
                    hostname = socket.getfqdn(ip_address)
                    access_time = line.split(' ')[0] + ' ' + line.split(' ')[1]
                    checkpath = Path(self._out)
                    if checkpath.exists():
                        if str(ip_address) in open(self._out).read():
                            self.update_ip(ip_address, access_time, hostname)
                        else:
                            self.new_ip(ip_address, access_time, hostname)
                    else:
                        self.first_ip(ip_address, access_time, hostname)
                    self._state = ip_address
                    stream = open(self._out, 'r')
                    geo_info = yaml.load(stream)
                    self._hostname = geo_info[ip_address]['hostname']
                    self._country = geo_info[ip_address]['country']
                    self._region = geo_info[ip_address]['region']
                    self._city = geo_info[ip_address]['city']
                    self._last_authenticated_time = geo_info[ip_address]['last_authenticated']
                    self._previous_authenticated_time = geo_info[ip_address]['previous_authenticated_time']
                else:
                    _LOGGER.debug("%s is in the exclude list, skipping update.", ip_address)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Last successful authentication'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return 'mdi:security-lock'

    @property
    def device_state_attributes(self):
        """Return attributes for the sensor."""
        return {
            ATTR_HOSTNAME: self._hostname,
            ATTR_COUNTRY: self._country,
            ATTR_REGION: self._region,
            ATTR_CITY: self._city,
            ATTR_NEW_IP: self._new_ip,
            ATTR_LAST_AUTHENTICATE_TIME: self._last_authenticated_time,
            ATTR_PREVIOUS_AUTHENTICATE_TIME: self._previous_authenticated_time,
        }
