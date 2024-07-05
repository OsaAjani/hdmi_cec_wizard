# hdmi_cec_wizard

`hdmi_cec_wizard` is a Python package designed to facilitate the use of HDMI-CEC in Python. It offers a programmatic wrapper for the `cec-ctl` tools, part of the `v4l-utils` project, enabling users to interact with HDMI-CEC devices using simple Python commands.

## Features

- Simplified access to HDMI-CEC functionalities
- Object-oriented style programming
- Easy auto-configuration
- Programmatically send CEC commands
- Retrieve information about connected HDMI-CEC devices
- Control device power states
- Request active source information

## Requirements

This module is fundamentally based on the `cec-ctl` and `cec-follower` tools from the `v4l-utils` project, meaning you have to install the `v4l-utils` package before installing this module.

This module is only compatible with UNIX systems.

## Installation

To install `hdmi_cec_wizard`, use pip:

```bash
pip install hdmi_cec_wizard
```

## Usage

To use this module you first have to create a Wizard and initialize it, the simplest way beeing the `autoconfig` method.
Once configured, you can access the `HDMICECWizard.local_device` to interract the connected HDMI devices.

```python
import time
from hdmi_cec_wizard import HDMICECWizard, CECButton, DeviceTypes

# Use wizard to start a cec-follower and configure a local cec-device on '/dev/cec0' of type playback with name "My custom name"
wizard = HDMICECWizard('/dev/cec0')
wizard.autoconfig(device_type = DeviceTypes.PLAYBACK, osd_name = "My custom name")

if not wizard.main_screen :
    raise Exception('Cannot find a connected screen')

# Turn on screen and try to get HDMI input
wizard.local_device.send_power_on(wizard.main_screen)

# Make known to everybody we are an active source
wizard.local_device.broadcast_active_source()

time.sleep(1)

# Simulate pressing button "arrow down"
wizard.local_device.send_button_press(wizard.main_screen, CECButton.DOWN)

time.sleep(1)

# Finally turn off screen (put it in standby mode)
wizard.local_device.send_power_off(wizard.main_screen)
```

For more information, take a look at the method docstrings
