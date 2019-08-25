# homeassistant-mi-water-purifier-1a
XiaoMi Water Purifier 1A component for Home Assistant.

![Screenshot](images/screenshot.png)

## Installation
1. Copy mi_water_purifier_1a into .homeassistant/custom_components/mi_water_purifier_1a
2. Get the IP of your sensor.
3. Follow [Retrieving the Access Token](https://home-assistant.io/components/vacuum.xiaomi_miio/#retrieving-the-access-token) guide to get the token of your sensor

## Configuration
```yaml
sensor:
  - platform: mi_water_purifier_1a
    host: YOUR_SENSOR_IP
    token: YOUR_SENSOR_TOKEN
    name: YOUT_SENSOR_NAME
```
