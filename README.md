# Custom Components for Home assistant
This repo contains my custom components for home assistant.

## Components
## JVC Projector
Supported commands,
* On/off
* Lens memory
* Input (HDMI Only)
* Power status

Requires my [jvc-projector-remote](https://github.com/bezmi/jvc_projector)
module to work.

### Support/features
#### Home Assistant Component
If you'd like home assistant specific support, or would like me to
implement/improve a feature for the homeassistant component, raise an issue and
I'll get around to it.

#### Python Module Support
If you would like a new command to be implemented, or have issues with related code, please raise
an issue in the [jvc-projector-remote](https://github.com/bezmi/jvc_projector) repo.

### Installation
#### Hassbian
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

#### Hass.io
1. Add this repository to your hass.io instance.
2. Install the "jvcprojector" addon.
3. Start the "jvcprojector" addon.
4. Check the logs for errors.
5. Configure the remote component based on instructions in the `jvcprojector` directory.


### Documentation/Examples
see the README in the `jvcprojector` directory.

# Disclaimer
I've used python for a long while in scientific work, but not too much for OOP. Be sure to let me know if there are improvements to be made to my code!
