"""Support for Xiaomi water purifier."""
import math
import logging

from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, )
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import PlatformNotReady
from miio import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-miio>=0.3.1']

CURRENT_TDS = {'name': 'Current TDS', 'key': 'tds_out'}
TDS_WARN_THD =  {'name': 'TDS warn thd', 'key': 'tds_warn_thd'}
TEMPERATURE = {'name': 'Temperature', 'key': 'temperature'}
AVERAGE_TDS = {'name': 'Average TDS', 'key': 'tds_out_avg'}
FILTER_PP_DAYS_REMAIN = {'name': '3in1 Filter days remaining', 'key': 'f1_usedtime', 'remain_days': 'pp_reamin'}
FILTER_RO_DAYS_REMAIN = {'name': 'RO Filter days remaining', 'key': 'f2_usedtime', 'remain_days': 'ro_reamin'}
FILTER_PP_FLOW_REMAIN = {'name': '3in1 Filter flow usage', 'key': 'f1_usedtime', 'remain_flow': 'pp_flow_remain'}
FILTER_RO_FLOW_REMAIN = {'name': 'RO Filter flow usage', 'key': 'f2_usedtime', 'remain_flow':'ro_flow_remain'}
	
AVAILABLE_PROPERTIES_COMMON = [
   'tds_out', 
   'temperature', 
   'f1_totalflow', 
   'f1_totaltime', 
   'f1_usedflow',
   'f1_usedtime', 
   'f2_totalflow', 
   'f2_totaltime', 
   'f2_usedflow', 
   'f2_usedtime',
   'run_status', 
   'rinse', 
   'tds_warn_thd', 
   'tds_out_avg']	

   
#[2, 29, 7200, 8640, 220, 5712, 7200, 17280, 220, 5712, 0, 0, 100, 100]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Xiaomi water purifier."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing Xiaomi water purifier with host %s (token %s...)", host, token[:5])

    devices = []
    try:
        device = Device(host, token)
        waterPurifier = XiaomiWaterPurifier(device, name)
        devices.append(waterPurifier)
    except DeviceException:
        _LOGGER.exception('Fail to setup Xiaomi water purifier')
        raise PlatformNotReady

    add_devices(devices)

class XiaomiWaterPurifierSensor(Entity):
    """Representation of a XiaomiWaterPurifierSensor."""

    def __init__(self, waterPurifier, data_key):
        """Initialize the XiaomiWaterPurifierSensor."""
        self._state = None
        self._data = None
        self._waterPurifier = waterPurifier
        self._data_key = data_key
        self.parse_data()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._data_key['name']

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._data_key['key'] is CURRENT_TDS['key'] or \
           self._data_key['key'] is AVERAGE_TDS['key']:
            return 'mdi:water'
        else:
            return 'mdi:filter-outline'

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        if self._data_key['key'] is CURRENT_TDS['key'] or \
           self._data_key['key'] is AVERAGE_TDS['key']:
            return 'TDS'
        return 'days'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}
        if self._data_key['key'] is FILTER_PP['key'] or \
           self._data_key['key'] is FILTER_RO['key']:
            attrs[self._data_key['name']] = '{} days remaining'.format(self._data[self._data_key['remain_key']])
                	 
        return attrs

    def parse_data(self):
        if self._waterPurifier._data:
            self._data = self._waterPurifier._data

    def update(self):
        """Get the latest data and updates the states."""
        self.parse_data()

  
class XiaomiWaterPurifier(Entity):
    """Representation of a XiaomiWaterPurifier."""

    def __init__(self, device, name):
        """Initialize the XiaomiWaterPurifier."""
        self._state = None
        self._device = device
        self._name = name
        self.parse_data()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:water'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return 'TDS'

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def hidden(self) -> bool:
        """Return True if the entity should be hidden from UIs."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}
        attrs[CURRENT_TDS['name']] = '{}TDS'.format(self._data[CURRENT_TDS['key']])
        attrs[TEMPERATURE['name']] = '{}°C'.format(self._data[TEMPERATURE['key']])
        attrs[AVERAGE_TDS['name']] = '{}TDS'.format(self._data[AVERAGE_TDS['key']])
        attrs[TDS_WARN_THD['name']] = '{}TDS'.format(self._data[TDS_WARN_THD['key']])
        attrs[FILTER_PP_DAYS_REMAIN['name']] = '{}Days'.format(self._data[FILTER_PP_DAYS_REMAIN['remain_days']])
        attrs[FILTER_RO_DAYS_REMAIN['name']] = '{}Days'.format(self._data[FILTER_RO_DAYS_REMAIN['remain_days']])
        attrs[FILTER_PP_FLOW_REMAIN['name']] = '{}L'.format(self._data[FILTER_PP_FLOW_REMAIN['remain_flow']])
        attrs[FILTER_RO_FLOW_REMAIN['name']] = '{}L'.format(self._data[FILTER_RO_FLOW_REMAIN['remain_flow']])
        return attrs

    def parse_data(self):
        """Parse data."""
        try:
            data = {}
            properties = AVAILABLE_PROPERTIES_COMMON
            _props_per_request = 1
            _props = properties.copy()
            values = []
            while _props:
              status = self._device.send("get_prop", _props[:_props_per_request])
              _props[:] = _props[_props_per_request:]          
              values.extend(status)
            values_count = len(values)
            print('finished ',values)            
            data[CURRENT_TDS['key']] = values[0]
            data[TEMPERATURE['key']] = values[1]
         
          
            data[FILTER_PP_DAYS_REMAIN['remain_days']] = int((values[3] - values[5]) / 24)
            data[FILTER_PP_FLOW_REMAIN['remain_flow']] = str(values[4]) + '/' + str(values[2])				
            
            
            data[FILTER_RO_DAYS_REMAIN['remain_days']] = int((values[7] - values[9]) / 24)
            data[FILTER_RO_FLOW_REMAIN['remain_flow']] = str(values[8]) + '/' + str(values[6])	

            data[AVERAGE_TDS['key']] = values[13]
            data[TDS_WARN_THD['key']]= values[12]
            self._data = data
            self._state = self._data[CURRENT_TDS['key']]
        except DeviceException:
            _LOGGER.exception('Fail to get_prop from Xiaomi water purifier')
            self._data = None
            self._state = None
            raise PlatformNotReady

    def update(self):
        """Get the latest data and updates the states."""
        self.parse_data()
