# JVC Projector Remote
The `jvcprojector` remote platform allows you to control the state of a JVC
Projector.

Known Supported Units:
* DLA-X5900

I have only tested on my own projector, but the IP command format hasn't changed
for a while and should work with most JVC D-ILA projectors.

To configure the remote component, add it under `remote` in your
`configuration.yaml`:
```yaml
# Example configuration.yaml entry
remote:
  - platform: jvcprojector
    name: Projector
    host: 192.168.1.14
```
### Configuration Variables
**name:** (string) (Required) friendly name for your projector.

**host:** (string) (Required) your projector IP address.

### Service `remote.turn_off`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

### Service `remote.turn_on`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |

### Service `remote.send_command`
| Service data attribute | Optional | Description |
| ---------------------- | -------- | ----------- |
| `entity_id`            |       no |Entity ID to projector. |
| `command`              |       no |A command to send. |

The available commands are:
* **Lens Memory:** `memory1`, `memory2`, `memory3`, `memory4`,`memory5`
* **Source:** `hdmi1`, `hdmi2`
* **Picture Mode:** `pm_cinema`, `pm_hdr`, `pm_natural`, `pm_film`, `pm_THX`, `pm_user{1-6}`, `pm_hlg`

Currently there is no feedback for these commands, but it is something that may be implemented in future. For power on/off, use the `remote.turn_on` and `remote.turn_off` services, as these retrieve the power state.

### Examples

You can implement changing of the projector input and lens memory based on `input_select` entities and some automation templates.

In `configuration.yaml`:
```yaml
# Example configuration.yaml for projector input source and lens memory
input_select:
  jvc_projector_input:
    name: Input
    options:
      - HDMI 1
      - HDMI 2
    initial: HDMI 1
  jvc_projector_memory:
    name: Lens Memory
    options:
      - Memory 1
      - Memory 2
      - Memory 3
      - Memory 4
      - Memory 5
```
In `automations.yaml`:
```yaml
  - alias: projector input
    trigger:
      platform: state
      entity_id: input_select.jvc_projector_input
    condition:
        - condition: state
          entity_id: remote.projector
          state: 'on'
    action:
      service: remote.send_command
      data_template:
        entity_id: remote.projector
        command: >-
            {% if is_state('input_select.jvc_projector_input', 'HDMI 1') %}
              hdmi1
            {% elif is_state('input_select.jvc_projector_input', 'HDMI 2') %}
              hdmi2
            {% endif %}

  - alias: projector memory
    trigger:
      platform: state
      entity_id: input_select.jvc_projector_memory
    condition:
        - condition: state
          entity_id: remote.projector
          state: 'on'
    action:
      service: remote.send_command
      data_template:
        entity_id: remote.projector
        command: >-
            {% if is_state('input_select.jvc_projector_memory', 'Memory 1') %}
              memory1
            {% elif is_state('input_select.jvc_projector_memory', 'Memory 2') %}
              memory2
            {% elif is_state('input_select.jvc_projector_memory', 'Memory 3') %}
              memory3
            {% elif is_state('input_select.jvc_projector_memory', 'Memory 4') %}
              memory4
            {% elif is_state('input_select.jvc_projector_memory', 'Memory 5') %}
              memory5
            {% endif %}
```
