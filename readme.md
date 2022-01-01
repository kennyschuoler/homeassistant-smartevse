# Smart EVSE - A Home Assistant custom component for Smart EVSE

## Installation

### Install with HACS (recomended)

If you have HACS (Home Assistant Community Store) installed, just search for Smart EVSE and install it direct from HACS.
HACS will keep track of updates and you can easly upgrade to the latest version when a new release is available.

If you don't have it installed, check it out here: [HACS](https://community.home-assistant.io/t/custom-component-hacs)

### Manual installation

Clone or copy the repository and copy the folder 'homeassistant-smartevse/custom_component/smartevse' into '[config dir]/custom_components'.
Install required python library with (adjust to suit your environment):

```sh
pip install smartevse
```

## Configuration

TODO 

### Configuration options

TODO 

## Enable debug logging

TODO 

For comprehensive debug logging you can add this to your `<config dir>/configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    smartevse.connection: debug
    custom_components.smartevse: debug
 ```

## Further help or contributions

TODO