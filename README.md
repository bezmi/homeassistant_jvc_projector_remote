<h1 align=center>About us</h1>
This project is looking for (co-)maintainers. Times change, I might end up with a different projector brand, JVC might change the command interface for a newer model that I don't have. Enough people use this component now that I think it's important to think about think about its future. I would be grateful to have people who are competent in python and have access to a JVC projector on board. If you're willing to help, submit a pull request implementing new features, fixing bugs or tidying up my terrible programming and documentation!
<br><br>

> If you'd like to support on-going work for this homeassistant component, you can [donate on ko-fi](https://ko-fi.com/bezmi) or [github sponsors](https://github.com/sponsors/bezmi).

<p align="left"> 

 <img src="https://img.shields.io/badge/python-323330?style=for-the-badge&logo=python&logoColor=F7DF1E">
 
# JVC projector remote for Homeassistant
this repo contains a remote implementation for jvc projectors. **For the most up-to-date documentation, [visit the main repository page](https://github.com/bezmi/homeassistant_jvc_projector_remote)**.

We also have a [home assistant community page](https://community.home-assistant.io/t/jvc-projector-component/123417).

The `jvcprojector` remote platform allows you to control the state of a JVC
Projector. 

Known supported units:
* DLA-X5900
* DLA-RS1000
* DLA-RS3100
* NZ Series

The IP command format hasn't changed
for a while and it should work with most JVC D-ILA projectors.

# Getting started
## Installation⏳
### HACS (recommended)📕
For easy installation and updates, use [HACS](https://hacs.xyz/) to install this custom component. The installation instructions for HASS are available [here](https://hacs.xyz/docs/setup/prerequisites). 

Once HACS is setup, go to Settings -> Custom Repositories and add the following Repository:
``` 
bezmi/homeassistant_jvc_projector_remote
```
And use type `Integration`.

After that, hit the 'add' button and search for/install the 'JVC Projector Remote' option. It is recommended you select the 'show beta releases' option and install the latest pre-release build shown in our [releases](https://github.com/bezmi/homeassistant_jvc_projector_remote/releases) as they contain the most up to date features. Don't install the 'master' option, as that will go off the master branch which you can expect to be highly experimental and might break at any time.

## Configuration
### Configuration variables
#### Required
|  | Type | Description             |
| ---------------------- | -------- | ----------------------- |
| `name`            | `string`       | friendly name for your projector |
| `host` | `string` | your projector IP address |
| `password` | `int` | Network password. Only required for some projectors. It will say in the network settings for the device |

#### Optional
| | Type | Description |
|-|------|-------------|
| `scan_interval` | `float` | how often to poll for updates (in seconds) |
| `port` | `int` | which port to connect to. Default is 20554 |
| `timeout` | `float` | how many seconds to wait for response from projector before a communciation error is called. Default is 10 seconds |
| `delay` | `int` | how many milliseconds to wait between consecutive commands. Default is 600 ms |
| `max_retries` | `int` | how many times to retry commands before connection error. Default is 10 |

#### Example `configuration.yaml` entry
Add this under `remote` in your `configuration.yaml` (NOTE: no web interface set up at the moment, there's an open issue for it):
```yaml
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
Once the configuration has been edited and you've restarted homeassistant, there should be a remote entity that you can add to your dashboard. Automations can be created through the homeassistant web interface, or you can implement changing of the projector input and lens memory based on `input_select` entities and some automation templates.

#### Example automation
**Note:** might not work on more recent builds of homeassistant, this part is still a WIP. Edit your `automations.yaml` (Thanks to [OtisPresley](https://community.home-assistant.io/t/jvc-projector-component/123417/32) for the instructions!):
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

# Details
## Extra state attributes
See the ['Read commands' table](#read-commands) for descriptions of the extra state attributes. In addition to these, the component reports:

**`last_commands_sent`:** a list of the commands sent when `remote.send_command` was last called on this entity

**`last_commands_response`:** a list of the responses from the projector for each command in `last_commands_sent`. If the command was a successful write command (no response from projector), then the element in this list will be the string `success`. Otherwise, it will be a string representing the response from the projector.

## Services
##### Service `remote.turn_off`:
| Service data attribute | Optional | Description             |
| ---------------------- | -------- | ----------------------- |
| `entity_id`            | no       | Entity ID to projector. |

##### Service `remote.turn_on`:
| Service data attribute | Optional | Description             |
| ---------------------- | -------- | ----------------------- |
| `entity_id`            | no       | Entity ID to projector. |

##### Service `remote.send_command`:
| Service data attribute | Optional | Description                                                   |
| ---------------------- | -------- | ------------------------------------------------------------- |
| `entity_id`            | no       | Entity ID to projector.                                       |
| `command`              | no       | A command (or list of commands) to send.                      |
| `delay_secs`           | yes      | The time in seconds to wait between each command in the list. |


## Command strings
##### Write commands
These command strings will perform an operation on the projector. The corresponding entry in the `last_commands_response` attribute will be `success` if the operation succeeded, or `failed` otherwise. Values in '{}' indicate multiple choices.
| Type                 | Commands                                                                                             | note                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Power**           | `power-{on,off}`                                                                                     | recommended to use the `remote.turn_on` and `remote.turn_off` services. |
| **Lens memory**     | `memory-{1-10}`                                                                                      | Not all projectors will have all 10                                     |
| **Source**          | `input-{hdmi1, hdmi2}`                                                                               |                                                                         |
| **Picture mode**     | `picture_mode-{cinema, natural, film, THX, hlg, hdr10, user{1-6}, hdr10p, pana_pq, frame_adapt_hdr}` | `hdr10p`, `pana_pq` and `frame_adapt_hdr` for NZ series only            |
| **Low latency mode** | `low_latency-{on, off}`                                                                              |                                                                         |
| **Mask**             | `mask-{off, custom1, custom2, custom3}`                                                              |                                                                         |
| **Lamp**             | `lamp-{high,low}`                                                                                    | `mid` for NZ series only                                                |
| **Menu controls**    | `menu-{menu, up, down, left, right, ok, back}`                                                       |                                                                         |
| **Lens aperture**    | `aperture-{off, auto1, auto2}`                                                                       |                                                                         |
| **Anamorphic**       | `anamorphic-{off, a, b, c, d}`                                                                       | `d` for NZ series only                                                  |

##### Read commands
These command strings will store the response from the projector in the corresponding element of the  `last_commands_response` attribute or `failed` otherwise
| Type                 | Commands       | Returns                                                                                           |
| -------------------- | -------------- | -------------------------------------------------------------------------------------------------- |
| **Power status<sup>1</sup>**     | `power`        | `lamp_on`, `standby`, `cooling`, `reserved`, `emergency`                              |  |
| **Input<sup>1</sup>**           | `input`        | `hdmi1, hdmi2`                                                                        |
| **Signal status<sup>1</sup>**           | `signal`        | `active_signal, no_signal`                                                                        |
| **Picture mode<sup>1</sup>**     | `picture_mode` | `cinema, natural, film, THX, hlg, hdr10, user{1-6}, hdr10p, pana_pq, frame_adapt_hdr` |
| **Low latency mode** | `low_latency`  | `on, off`                                                                             |
| **Mask**             | `mask`         | `off, custom1, custom2, custom3`                                                      |
| **Lamp<sup>1</sup>**             | `lamp`         | `high, low`                                                                         |
| **Lens aperture**    | `aperture`     | off, auto1, auto2`                                                                   |
| **Anamorphic**       | `anamorphic`   | `off, a, b, c`, **NZ Series:** `d`                                                    |
| **MAC address**      | `macaddr`      | projector MAC address                                                                |
| **Model info**       | `modelinfo`    | model string of the projector                                                          |

<sup>1</sup> These are reported in the extra state attributes.



# Support🤝
Check out the [Home Assistant Community Page](https://community.home-assistant.io/t/jvc-projector-component/123417) and the [discussion board](https://github.com/bezmi/homeassistant_jvc_projector_remote/discussions) if you're having trouble getting this working.

### Any issues? ☠
If you'd like home assistant specific support, or would like me to
implement a feature for the homeassistant component, post on the [discussion board](https://github.com/bezmi/homeassistant_jvc_projector_remote/discussions).

For problems with getting this to work with homeassistant, post on the [discussion board](https://github.com/bezmi/homeassistant_jvc_projector_remote/discussions) first. That way we can [raise an issue](https://github.com/bezmi/homeassistant_jvc_projector_remote/issues/new/choose) once we've identified actual bugs, whilst keeping tech support questions out of the issue tracker.

If you would like a new command to be implemented, please raise
an issue in the [jvc-projector-remote](https://github.com/bezmi/jvc_projector) repo, or don't, and just report it here. I'm sure we'll figure it out.
<br><br>

### For folks who want to contribute ❤
[Check out the open issues](https://github.com/bezmi/homeassistant_jvc_projector_remote/issues)

Fork this repo and create a pull request &nbsp;🌈 &nbsp; ✨

Your contribution is highly appreciated 🙏.</br>
<div align="center">
<h4 font-weight="bold">This repository is maintained by <a href="https://github.com/bezmi">bezmi</a></h4>
<p> Show some ❤️ by giving us a star! </p>
</div>

