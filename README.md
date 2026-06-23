# GlobalTrack Vehicle Tracker

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/demoklion/home-assistant-globaltrack)](https://github.com/demoklion/home-assistant-globaltrack/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

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

This integration is available in the **default HACS store** — no custom repository needed.

1. Open HACS in your Home Assistant instance
2. Search for **GlobalTrack**
3. Click **Download**
4. Restart Home Assistant

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
        entity_id: sensor.globaltrack_my_car_battery_voltage
        below: 12.0
        for: "00:30:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Low car battery"
          message: "Vehicle battery is at {{ states('sensor.globaltrack_my_car_battery_voltage') }} V"
```

## Disclaimer

This is an unofficial, community-maintained integration. It is not affiliated with, endorsed by, or connected to GlobalTrack, LogisCarE, or GlobalSec. The integration relies on undocumented APIs and may break if the platform changes.

## Author

Built by [Ján Dugovič](https://jandu.top) with [Claude Code](https://claude.com/claude-code).

## License

[GPL-3.0](LICENSE)
