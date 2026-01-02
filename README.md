# Windows and Doors Summary for Home Assistant

Provides a single aggregated **binary sensor** that reports whether any relevant doors or windows in your home are open.

The integration is designed to support alarm and notification use cases, where some openings (e.g. front door, windows) are critical, while others (e.g. shed or garage) are informational only.

---

## What this integration does

The integration monitors:

- Any number of **door** sensors
- Any number of **window** sensors
- Any number of **special openings** (e.g. shed door, garage door)

It exposes **one binary sensor** with rich attributes.

---

## Binary sensor

| Name | Possible states | Explanation |
|-----|-----------------|-------------|
| State | on / off | `on` if **any door or window** is open. `off` if all doors and windows are closed. |

Special openings **never affect** the sensor state.

---

## Attributes

| Attribute | Type | Explanation |
|---------|------|-------------|
| `number_of_doors` | integer | Number of doors currently open |
| `number_of_windows` | integer | Number of windows currently open |
| `list_of_open` | list | Human-readable names of all open doors and windows |
| `last_door_opened` | string | Name of the last door that was opened |
| `door_opened_at` | string | Local timestamp (`YYYY-MM-DDTHH:MM:SS`) of last door opening |
| `<custom_name>` | string | State (`Open`, `Closed`, `Unknown`) of each special opening |

Custom attribute names for special openings are derived from the names you provide during setup (e.g. `shed_door`, `garage_door`).

---

## Installation

### Option 1: HACS (recommended)

1. Go to **HACS → Integrations**
2. Click the three dots in the top-right corner
3. Select **Custom repositories**
4. Add this repository URL: https://github.com/Aephir/ha-windows-and-doors
5. Select **Integration** as the category
6. Click **Add**
7. Search for **Windows and Doors Summary** and install it
8. Restart Home Assistant

---

### Option 2: Manual installation

Download the latest release from GitHub and extract it into your Home Assistant configuration directory:

```bash
cd YOUR_HASS_CONFIG_DIRECTORY  # same directory as configuration.yaml
mkdir -p custom_components/windows_and_doors
cd custom_components/windows_and_doors
unzip windows_and_doors-X.Y.Z.zip
mv windows_and_doors-X.Y.Z/custom_components/windows_and_doors/* .
```

Restart Home Assistant.

Setup
1.	Go to Settings → Devices & Services
2.	Click + Add Integration
3.	Search for Windows and Doors Summary
4.	Select it and follow the setup wizard

Setup inputs

During setup you will be asked to provide:

Door sensors
- One or more binary_sensor entities
- These are considered critical openings
- Door openings are tracked for:
- Count
- Alarm state
- Last door opened

Window sensors
- One or more binary_sensor entities
- Windows affect the alarm state but are not tracked as “last opened”

Special openings (optional)
- Any number of binary_sensor entities
- Each requires a custom name (e.g. “Shed door”, “Garage door”)
- Special openings:
- Appear only as attributes
- Never affect the binary sensor state
- Never trigger alarms or notifications

This makes it possible to ignore less critical openings while still keeping visibility.

⸻

Adding or changing sensors after setup

To add, remove, or change doors, windows, or special openings:
1.	Go to Settings → Devices & Services
2.	Find Windows and Doors Summary
3.	Click Configure
4.	Update the lists as needed and submit

No YAML changes or restarts are required.

⸻

Supported sensor states

The integration treats the following states as “open”:
- on
- open
- opening

This makes it compatible with a wide range of door and window sensors.

⸻

Typical use cases
- Alarm notifications when leaving home with a door or window open
- Lovelace badge showing whether any openings are open
- Human-readable notifications using last_door_opened
- Ignoring shed or garage doors for alarms while still showing their state

⸻

Notes and limitations
- Special openings do not count toward door/window totals by design
- Only doors are tracked for “last opened”
- The integration assumes one entity per physical opening