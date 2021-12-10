# JVC Projector IP Control component for Home Assistant

This is a custom [Home Assistant](https://home-assistant.io/) component to support IP control of JVC projectors. This should work with nearly any recent JVC projector as the IP control schema has not changed for some time. Check out the [Home Assistant community page](https://community.home-assistant.io/t/jvc-projector-component/123417) for support.

Supported Commands:

- Power on/off
- Lens Memory
- Input (HDMI only)
- Power Status (Standby, Cooling, Emergency, Lamp On, Reserved)
- Picture Modes (Cinema, HDR, Natural, Film, THX, User{1-6}, HLG)
- Low Latency Enable/Disable
- Mask (Custom{1-3}, Off)
- Lamp High/Low
- Menu Controls (Menu, Up, Down, Left, Right, OK, Back)
- Lens Aperture (Off, Auto 1, Auto 2)
- Anamorphic (Off, a, b, c)

For first time setup and configuration steps, refer to the [documentation](https://github.com/bezmi/hass_custom_components/blob/master/custom_components/jvcprojector/README.md).
