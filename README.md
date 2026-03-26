# GlobalTrack Vehicle Tracker

Home Assistant integration for [GlobalTrack](https://www.globaltrack.cz) / LogisCarE Commander vehicle tracking platforms.

## Features

- **Device tracker** — vehicles appear on the HA map with real-time GPS position
- **Battery voltage** sensor (V)
- **Odometer** sensor (km)
- **Speed** sensor (km/h)
- **Address** sensor — last known location as text
- **Ignition** binary sensor — engine on/off

All entities update every 60 seconds via cloud polling.

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations** > three-dot menu > **Custom repositories**
3. Add this repository URL, category: **Integration**
4. Search for "GlobalTrack" and install
5. Restart Home Assistant

### Manual

Copy the `custom_components/globaltrack` folder into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **GlobalTrack**
3. Enter your credentials:
   - **Email** — your GlobalTrack / LogisCarE login email
   - **Password** — your account password
   - **Portal URL** — defaults to `https://www2.globaltrack.cz` (change only if you use a different LogisCarE instance)

## Example automation: low battery alert

```yaml
automation:
  - alias: "Car battery low voltage"
    trigger:
      - platform: numeric_state
        entity_id: sensor.globaltrack_vw_tiguan_battery_voltage
        below: 12.0
        for: "00:30:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Low car battery"
          message: "Vehicle battery is at {{ states('sensor.globaltrack_vw_tiguan_battery_voltage') }} V"
```

## Disclaimer

This is an unofficial, community-maintained integration. It is not affiliated with, endorsed by, or connected to GlobalTrack, LogisCarE, or GlobalSec. The integration relies on undocumented APIs and may break if the platform changes.

## License

[MIT](LICENSE)
