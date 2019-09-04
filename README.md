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
#### HACS (Preferred)
For easy installation and updates, use the [Home Assistant Community Store](https://github.com/custom-components/hacs) to install this custom component. 
HACS will download and install the custom component for you and keep track of updates.

Once HACS is setup, go to Settings -> Custom Repositories and add the following Repository:
``` 
bezmi/hass_custom_components
```

And use type `Integration`. Once installed, proceed to follow README in the 'jvcprojector' directory.

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
```
#### Hass.io
1. SSH into your Hass.io instance. I recommend the community SSH addon, see its documentation for instructions.
2. Clone this repo:
~~~
git clone https://github.com/bezmi/hass_custom_components
~~~
3. Make a `custom_components` directory if one doesn't exist
~~~
mkdir /config/custom_components
~~~
4. Copy the folder for your desired component into the `custom_components` directory,
~~~
cp -r ./hass_custom_components/custom_components/jvcprojector /config/custom_components
~~~
5. Restart Hass.io


### Documentation/Examples
see the README in the `jvcprojector` directory.

# Disclaimer
I've used python for a long while in scientific work, but not too much for OOP. Be sure to let me know if there are improvements to be made to my code!
