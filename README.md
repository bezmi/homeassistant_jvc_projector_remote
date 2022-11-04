This project is looking for (co-)maintainers. Times change, I might end up with a different projector brand, JVC might change the command interface for a newer model that I don't have. Enough people use this component now that I think it's important to think about think about its future. I would be grateful to have people who are competent in python and have access to a JVC projector on board. If you're willing to help, submit a pull request implementing new features, fixing bugs or tidying up my terrible programming and documentation!

If you'd like to support on-going work for this homeassistant component, you can [donate on ko-fi](https://ko-fi.com/bezmi). 

# JVC Projector Remote for Homeassistant
this repo contains a remote implementation for jvc projectors.

Check out the [Home Assistant Community Page](https://community.home-assistant.io/t/jvc-projector-component/123417) if you're having trouble getting this working.

The `jvcprojector` remote platform allows you to control the state of a JVC
Projector. 

DISCLAIMER: I rarely have time to work on these things, so if anything is broken, let me know and I'll push out a patch as quickly as possible. Alternatively, create a pull request!

Known Supported Units:
* DLA-X5900
* DLA-RS1000
* DLA-RS3100

The IP command format hasn't changed
for a while and it should work with most JVC D-ILA projectors.

**NOTE For JVC NZ series**
JVC has implemented a "Network Password" with their latest projectors (NZ Series). You will need to define a Network Password on the projector and provide it in the configuration of this integration in order for it to communicate.

## Basic Setup and Example Usage
Add this under `remote` in your `configuration.yaml` (NOTE: no web interface set up at the moment, there's an open issue for it):
```yaml
# Example configuration.yaml entry
remote:
  - platform: jvcprojector
    name: Projector
    host: 192.168.1.14
    scan_interval: 30

    # only required for NZ series and up
    password: MyPassword

    # optional, default is 20554
    port: 20554

    # optional, float, default is 0.5 seconds
    # how long to wait before raising a communication error
    timeout: 0.5

    # how long to wait between commands
    # optional, default is 600 milliseconds
    delay: 600

    # how many times to retry on connection error
    # optional, default is 5
    max_retries: 5
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
              input-hdmi1
            {% elif is_state('input_select.jvc_projector_input', 'HDMI 2') %}
              input-hdmi2
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

### Configuration

#### Configuration Variables
**name:** (string) (Required) friendly name for your projector.

**host:** (string) (Required) your projector IP address.

**scan_interval:** (string) (Optional) timeout used to update the component

**password:** (string) (Optional) only required for NZ series (or up) projectors

**port:** (int) (Optional) which port to connect to, default is 20554

**timeout:** (float) (Optional) how many seconds to wait for response from projector before a communication error is called, default is 2.0 seconds

**delay:** (int) (Optional) how many milliseconds to wait between consecutive commands, default is 600 milliseconds

**max_retries:** (int) (Optional) how many times to retry connection on a socket error, default is 5

#### Extra State Attributes:
**`last_commands_sent`:** a list of the commands sent when `remote.send_command` was last called on this entity

**`last_commands_response`:** a list of the responses from the projector for each command in `last_commands_sent`. If the command was a successful write command (no response from projector), then the element in this list will be the string `success`. Otherwise, it will be a string representing the response from the projector.

**`power_state`:** the current power state of the projector. Will be one of: `lamp_on`, `reserved`, `standby`, `cooling`, `emergency`

**`signal_state`:** the current status of the input signal. Will be one of: `no_signal`, `active_signal`

**`input_state`:** the current input setting of the projector. Will be one of: `hdmi1`, `hdmi2`

**`lamp_state`:** the state of the lamp. Will be one of: `high`, `low`

**`picture_mode`:** the current picture mode setting. Will be one of: `cinema`, `natural`, `film`, `THX`, `hlg`, `hdr10`, `user{1-6}`

#### Service `remote.turn_off`:
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

#### Service `remote.turn_on`:
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

#### Service `remote.send_command`:
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |
| `command`              |       no |A command (or list of commands) to send. |
| `delay_secs`              |       yes |The time in seconds to wait between each command in the list. |


#### Command Strings:
These command strings will perform an operation on the projector. The corresponding entry in the `last_commands_response` attribute will be `success` if the operation succeeded, or `failed` otherwise. Values in '{}' indicate multiple choices.
* **Power:** `power-{on,off}` (recommended to use the `remote.turn_on` and `remote.turn_off` services).
* **Lens Memory:** `memory-{1-5}`
* **Source:** `input-{hdmi1, hdmi2}`
* **Picture Mode:** `picture_mode-{cinema, natural, film, THX, hlg, hdr10}`, `picture_mode-{user1-user6}`
* **Low Latency Mode:** `low_latency-{on, off}`
* **Mask** `mask-{off, custom1, custom2, custom3}`
* **Lamp** `lamp-{high,low}`
* **Menu Controls** `menu-{menu, up, down, left, right, ok, back}`
* **Lens Aperture** `aperture-{off, auto1, auto2}`
* **Anamorphic** `anamorphic-{off, a, b, c}`

These command strings will store the response from the projector in the corresponding element of the  `last_commands_response` attribute or `failed` otherwise:
* **Power status:** `power`, returns from `lamp_on`, `standby`, `cooling`, `reserved`, `emergency`
* **Source:** `input`, returns from `hdmi1, hdmi2`
* **Picture Mode:** `picture_mode`, returns from `cinema, natural, film, THX, hlg, hdr10, user{1-6}`
* **Low Latency Mode:** `low_latency`, returns from `on, off`
* **Mask** `mask`, returns from `off, custom1, custom2, custom3`
* **Lamp** `lamp`, returns from `high, low`
* **Lens Aperture** `aperture`, returns from `off, auto1, auto2`
* **Anamorphic** `anamorphic`, returns from `off, a, b, c`
* **MAC Address** `macaddr`, returns the projector's MAC address
* **Model Info** `modelinfo`, returns the model string of the projector

### Support
Check out the [Home Assistant Community Page](https://community.home-assistant.io/t/jvc-projector-component/123417) if you're having trouble getting this working.

#### Home Assistant Component
If you'd like home assistant specific support, or would like me to
implement/improve a feature for the homeassistant component, raise an issue and
I'll get around to it.

#### Python Module Support
If you would like a new command to be implemented, or have issues with related code, please raise
an issue in the [jvc-projector-remote](https://github.com/bezmi/jvc_projector) repo.
