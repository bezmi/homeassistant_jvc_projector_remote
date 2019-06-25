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
If you'd like home assistant specific support, or would like me to
implement/improve a feature for the homeassistant component, raise an issue and
I'll get around to it. If you would like a remote command to be implemented, please raise
an issue in the [jvc-projector-remote](https://github.com/bezmi/jvc_projector) repo.

### Installation
For hassbian,

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
### Documentation/Examples
see the README in the `jvcprojector` directory.
