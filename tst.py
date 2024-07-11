from hdmi_cec_wizard import *
a=HDMICECWizard()
print(type(a))
a.autoconfig(DeviceTypes.PLAYBACK, 'MASET')
