# JVC Projector Remote for Homeassistant
this repo contains a remote implementation for jvc projectors.

Check out the [Home Assistant Community Page](https://community.home-assistant.io/t/jvc-projector-component/123417) if you're having trouble getting this working.

The `jvcprojector` remote platform allows you to control the state of a JVC
Projector. 

DISCLAIMER: I rarely have time to work on these things, so if anything is broken, let me know and I'll push out a patch as quickly as possible. Alternatively, create a pull request!

Known Supported Units:
* DLA-X5900
* DLA-RS1000

The IP command format hasn't changed
for a while and it should work with most JVC D-ILA projectors.

## Basic Setup and Example Usage
Add this under `remote` in your `configuration.yaml` (NOTE: no web interface set up at the moment, there's an open issue for it):
```yaml
# Example configuration.yaml entry
remote:
  - platform: jvcprojector
    name: Projector
    host: 192.168.1.14
    scan_interval: 30
```
You can implement changing of the projector input and lens memory based on `input_select` entities and some automation templates.

Edit your `automations.yaml` (Thanks to [OtisPresley](https://community.home-assistant.io/t/jvc-projector-component/123417/32) for the updated instructions!):
```yaml
  - alias: projector input
    trigger:
      platform: state
      entity_id: input_select.jvc_projector_input
    condition:
        - condition: state
          entity_id: remote.theater_room_projector
          state: 'on'
    action:
      service: remote.send_command
      data_template:
        entity_id: remote.theater_room_projector
        command: >-
            {% if is_state('input_select.jvc_projector_input', 'HDMI 1') %}
              hdmi1
            {% elif is_state('input_select.jvc_projector_input', 'HDMI 2') %}
              hdmi2
            {% endif %}
```

Make sure the `entitity_id` matches your projector. You can go to **Developer Settings** and under **Services**, use the `Remote:Turn on` service to select the entity. Then use **GO TO YAML MODE** to see the `entity_id`.

Add an **Entities** card to your dashboard to control it. Make sure the inputs switch stays on to be able to change projector inputs.

**IMPORTANT NOTE:** In your projector settings, you must make sure that the Control4 setting is turned OFF under Network options. While this is on, the projector will not expose port 20554, which means this integration won’t work.

## Installation
### HACS (Recommended)
For easy installation and updates, use [HACS](https://hacs.xyz/) to install this custom component. The installation instructions for HASS are available [here](https://hacs.xyz/docs/setup/prerequisites). 

After you've enabled HACS

Once HACS is setup, go to Settings -> Custom Repositories and add the following Repository:
``` 
bezmi/hass_custom_components
```

And use type `Integration`. Once installed, proceed to follow README in the 'jvcprojector' directory.

### Hassbian (Advanced)
This is for experienced users only, I won't provide support for these installs because there are too many variables.
Clone this repo and copy the `jvcprojector` directory to,
~~~
<config_dir>/custom_components/
~~~
My `<config_dir>` is `/home/homeassistant/.homeassistant/`

Install the `jvc-projector-remote` python module. For hassbian,

``` shell
sudo -u <homeassistant> -H -s
source /srv/homeassistant/bin/activate
pip install jvc-projector-remote
```

### Configuration

#### Configuration Variables
**name:** (string) (Required) friendly name for your projector.

**host:** (string) (Required) your projector IP address.

**scan_interval:** (string) (Optional) timeout used to update the component (strong suggestion to set this to 30 or higher)

#### Service `remote.turn_off`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

#### Service `remote.turn_on`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

#### Service `remote.send_command`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |
| `command`              |       no |A command to send. |

The available commands are:
* **Lens Memory:** `memory1`, `memory2`, `memory3`, `memory4`,`memory5`
* **Source:** `hdmi1`, `hdmi2`
* **Picture Mode:** `pm_cinema`, `pm_hdr`, `pm_natural`, `pm_film`, `pm_THX`, `pm_user{1-6}`, `pm_hlg`
* **Low Latency Mode:** `pm_low_latency_enable`, `pm_low_latency_disable`
* **Mask** `mask_off`, `mask_custom{1,2,3}`
* **Lamp** `lamp_{high,low}`
* **Menu Controls** `menu`, `menu_{up,down,left,right,ok,back}`
* **Lens Aperture** `aperture_off`, `aperture_auto{1,2}`
* **Anamorphic** `anamorphic_off`, `anamorphic_{a,b,c}`

Currently there is no feedback for these commands. For power on/off, use the `remote.turn_on` and `remote.turn_off` services, as these retrieve the power state.

### Support
Check out the [Home Assistant Community Page](https://community.home-assistant.io/t/jvc-projector-component/123417) if you're having trouble getting this working.

#### Home Assistant Component
If you'd like home assistant specific support, or would like me to
implement/improve a feature for the homeassistant component, raise an issue and
I'll get around to it.

#### Python Module Support
If you would like a new command to be implemented, or have issues with related code, please raise
an issue in the [jvc-projector-remote](https://github.com/bezmi/jvc_projector) repo.
