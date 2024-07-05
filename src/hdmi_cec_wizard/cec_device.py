from enum import Enum
import subprocess
from subprocess import CompletedProcess
import shlex
import re
from exceptions import *


class CECButton(Enum):
    SELECT = {"str": "select", "code": "0x00"}
    UP = {"str": "up", "code": "0x01"}
    DOWN = {"str": "down", "code": "0x02"}
    LEFT = {"str": "left", "code": "0x03"}
    RIGHT = {"str": "right", "code": "0x04"}
    RIGHT_UP = {"str": "right-up", "code": "0x05"}
    RIGHT_DOWN = {"str": "right-down", "code": "0x06"}
    LEFT_UP = {"str": "left-up", "code": "0x07"}
    LEFT_DOWN = {"str": "left-down", "code": "0x08"}
    DEVICE_ROOT_MENU = {"str": "device-root-menu", "code": "0x09"}
    DEVICE_SETUP_MENU = {"str": "device-setup-menu", "code": "0x0a"}
    CONTENTS_MENU = {"str": "contents-menu", "code": "0x0b"}
    FAVORITE_MENU = {"str": "favorite-menu", "code": "0x0c"}
    BACK = {"str": "back", "code": "0x0d"}
    MEDIA_TOP_MENU = {"str": "media-top-menu", "code": "0x10"}
    MEDIA_CONTEXT_SENSITIVE_MENU = {"str": "media-context-sensitive-menu", "code": "0x11"}
    NUMBER_ENTRY_MODE = {"str": "number-entry-mode", "code": "0x1d"}
    NUMBER_11 = {"str": "number-11", "code": "0x1e"}
    NUMBER_12 = {"str": "number-12", "code": "0x1f"}
    NUMBER_0_OR_NUMBER_10 = {"str": "number-0-or-number-10", "code": "0x20"}
    NUMBER_1 = {"str": "number-1", "code": "0x21"}
    NUMBER_2 = {"str": "number-2", "code": "0x22"}
    NUMBER_3 = {"str": "number-3", "code": "0x23"}
    NUMBER_4 = {"str": "number-4", "code": "0x24"}
    NUMBER_5 = {"str": "number-5", "code": "0x25"}
    NUMBER_6 = {"str": "number-6", "code": "0x26"}
    NUMBER_7 = {"str": "number-7", "code": "0x27"}
    NUMBER_8 = {"str": "number-8", "code": "0x28"}
    NUMBER_9 = {"str": "number-9", "code": "0x29"}
    DOT = {"str": "dot", "code": "0x2a"}
    ENTER = {"str": "enter", "code": "0x2b"}
    CLEAR = {"str": "clear", "code": "0x2c"}
    NEXT_FAVORITE = {"str": "next-favorite", "code": "0x2f"}
    CHANNEL_UP = {"str": "channel-up", "code": "0x30"}
    CHANNEL_DOWN = {"str": "channel-down", "code": "0x31"}
    PREVIOUS_CHANNEL = {"str": "previous-channel", "code": "0x32"}
    SOUND_SELECT = {"str": "sound-select", "code": "0x33"}
    INPUT_SELECT = {"str": "input-select", "code": "0x34"}
    DISPLAY_INFORMATION = {"str": "display-information", "code": "0x35"}
    HELP = {"str": "help", "code": "0x36"}
    PAGE_UP = {"str": "page-up", "code": "0x37"}
    PAGE_DOWN = {"str": "page-down", "code": "0x38"}
    POWER = {"str": "power", "code": "0x40"}
    VOLUME_UP = {"str": "volume-up", "code": "0x41"}
    VOLUME_DOWN = {"str": "volume-down", "code": "0x42"}
    MUTE = {"str": "mute", "code": "0x43"}
    PLAY = {"str": "play", "code": "0x44"}
    STOP = {"str": "stop", "code": "0x45"}
    PAUSE = {"str": "pause", "code": "0x46"}
    RECORD = {"str": "record", "code": "0x47"}
    REWIND = {"str": "rewind", "code": "0x48"}
    FAST_FORWARD = {"str": "fast-forward", "code": "0x49"}
    EJECT = {"str": "eject", "code": "0x4a"}
    SKIP_FORWARD = {"str": "skip-forward", "code": "0x4b"}
    SKIP_BACKWARD = {"str": "skip-backward", "code": "0x4c"}
    STOP_RECORD = {"str": "stop-record", "code": "0x4d"}
    PAUSE_RECORD = {"str": "pause-record", "code": "0x4e"}
    ANGLE = {"str": "angle", "code": "0x50"}
    SUB_PICTURE = {"str": "sub-picture", "code": "0x51"}
    VIDEO_ON_DEMAND = {"str": "video-on-demand", "code": "0x52"}
    ELECTRONIC_PROGRAM_GUIDE = {"str": "electronic-program-guide", "code": "0x53"}
    TIMER_PROGRAMMING = {"str": "timer-programming", "code": "0x54"}
    INITIAL_CONFIGURATION = {"str": "initial-configuration", "code": "0x55"}
    SELECT_BROADCAST_TYPE = {"str": "select-broadcast-type", "code": "0x56"}
    SELECT_SOUND_PRESENTATION = {"str": "select-sound-presentation", "code": "0x57"}
    AUDIO_DESCRIPTION = {"str": "audio-description", "code": "0x58"}
    INTERNET = {"str": "internet", "code": "0x59"}
    MODE_3D = {"str": "3d-mode", "code": "0x5a"}
    PLAY_FUNCTION = {"str": "play-function", "code": "0x60"}
    PAUSE_PLAY_FUNCTION = {"str": "pause-play-function", "code": "0x61"}
    RECORD_FUNCTION = {"str": "record-function", "code": "0x62"}
    PAUSE_RECORD_FUNCTION = {"str": "pause-record-function", "code": "0x63"}
    STOP_FUNCTION = {"str": "stop-function", "code": "0x64"}
    MUTE_FUNCTION = {"str": "mute-function", "code": "0x65"}
    RESTORE_VOLUME_FUNCTION = {"str": "restore-volume-function", "code": "0x66"}
    TUNE_FUNCTION = {"str": "tune-function", "code": "0x67"}
    SELECT_MEDIA_FUNCTION = {"str": "select-media-function", "code": "0x68"}
    SELECT_AV_INPUT_FUNCTION = {"str": "select-av-input-function", "code": "0x69"}
    SELECT_AUDIO_INPUT_FUNCTION = {"str": "select-audio-input-function", "code": "0x6a"}
    POWER_TOGGLE_FUNCTION = {"str": "power-toggle-function", "code": "0x6b"}
    POWER_OFF_FUNCTION = {"str": "power-off-function", "code": "0x6c"}
    POWER_ON_FUNCTION = {"str": "power-on-function", "code": "0x6d"}
    F1_BLUE = {"str": "f1-blue", "code": "0x71"}
    F2_RED = {"str": "f2-red", "code": "0x72"}
    F3_GREEN = {"str": "f3-green", "code": "0x73"}
    F4_YELLOW = {"str": "f4-yellow", "code": "0x74"}
    F5 = {"str": "f5", "code": "0x75"}
    DATA = {"str": "data", "code": "0x76"}


class DeviceTypes(Enum):
        """
            Available types of HDMI CEC devices
        """
        TV = {'str': 'TV', 'param': '--tv'}  # Television device
        RECORDER = {'str': 'Recorder', 'param': '--record'}  # Device that records content (DVR)
        TUNER = {'str': 'Tuner', 'param': '--tuner'}  # Device that tunes and receives broadcast signals
        PLAYBACK = {'str': 'Playback', 'param': '--playback'}  # Device that plays audio or video content
        AUDIO = {'str': 'Audio', 'param': '--audio'}  # Device focused on audio playback or processing
        AMPLIFIER = {'str': 'Amplifier', 'param': '--amplifier'}  # Device that amplifies audio signals
        SWITCH = {'str': 'Switch', 'param': '--switch'}  # Device that switches HDMI inputs
        PROCESSOR = {'str': 'Processor', 'param': '--processor'}  # Device that processes audio or video signals


class CECDevice ():
    """
        This class is the describe a CEC device

        :param cec_version: Supported version of the CEC protocol
        :physical_address: Physical address of the device (a.k.a the physical HDMI port it is connected to)
        :logical_address: Logical address of the device, this is the address we will use to send command
        :device_type: The type of device, one of DeviceTypes.
        :vendor_id: The ID of the vendor as assigned by "HDMI Licensing, LLC", some vendor might fake it but its still a usefull info
        :power_status: Is the device power on or off, one of (On, Off, Standby). Standby is a low power mode, powered but not actively performing tasks.
        :osd_name: The human readable name of the device. Might be None.
    """
    def __init__(self, cec_version: str, physical_address: str , logical_address: str, device_type: DeviceTypes, vendor_id: str, power_status: str, osd_name: str = None) -> None:
        self.cec_version = cec_version
        self.physical_address = physical_address
        self.logical_address = logical_address
        self.device_type = device_type
        self.vendor_id = vendor_id
        self.power_status = power_status
        self.osd_name = osd_name


class LocalCECDevice (CECDevice):
    """
        This class describe a **Local** CEC device, meaning a CEC device we have a direct /dev/cecX handle on to control with cec-ctl
        Basically a LocalCECDevice is the device we use to send and receive commands to/from every other devices  

        **
        quick note: 
            If a method start with broadcast then its a message/question to everybody
            if it start with ask is a question to a specific device
            if it start with send its an order/response to a specific device
        **

        :cec_handle: Path to the /dev/cecX UNIX device we use with cec-ctl. Only provided for 
        :params: All the other params from CECDevice applies
    """

    REGEX_RESPONSE_PWR_STATE = r'\s+pwr-state:\s+(\w+)\s+\(\w+\)'
    REGEX_RESPONSE_TIMEOUT = r',\s+Timeout'
    REGEX_RESPONSE_FROM = r'\s+Received from .+ (\(\d+\))'
    REGEX_RESPONSE_PHYSICAL_ADDRESS = r'\s+phys-addr: (\w+\.\w+\.\w+\.\w+)'

    def __init__(self, cec_handle: str, *args, **kwargs) -> None:
        self.cec_handle = cec_handle
        super().__init__(*args, **kwargs)


    def run_cec_ctl(self, command_args: list, skip_info: bool = True) -> CompletedProcess:
        """
            Run a cec-ctl command from this device and return result
            :param command_args: Parameters to pass to cec-ctl command. 
                all args will be escaped with shlex.join

            :param skip_info: If True skip the driver info output in response. True by default

            :raise: Raise a CalledProcessError exception if cec-ctl command process return an error code
        """
        command_parts = ['cec-ctl', '-d', self.cec_handle]
        if skip_info :
            command_parts.append('--skip-info')
        
        command = shlex.join(command_parts + command_args)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        result.check_returncode()
        return result
    

    def send_cec_command_to(self, to: CECDevice, opcode: str, payload: str = None) -> CompletedProcess:
        """
            Send a CEC command to a specific device using his logical address
            :param to: The CECDevice to send the command to
            :param opcode: The CEC command opcode, as a string. Ex: 0x44 (press button)
            :param payload: The command paylod if any (including operands if any). By default None.
                Ex: 0x41 -> Volume up for press button, or 0x10:0x00 for the address part of the active-source command
        
            :raise: Raise a CalledProcessError exception if cec-ctl command process return an error code
        """
        cmd = 'cmd={}'.format(opcode)
        if payload :
            cmd = '{},payload={}'.format(cmd, payload)

        return self.run_cec_ctl(['--to', to.logical_address, '--custom-command', cmd])
    

    def send_button_press(self, to: CECDevice, button: CECButton) -> CompletedProcess:
        """
            Send a CEC command emulating a user pressing a button to the specified device

            Some device will always consider a button press to be a single press, while other might consider
            it to be a button hold (most notably volume up and down) you might then need to follow this with 
            a send_button_release call

            :param to: The CECDevice to send the button press to
            :param button: The button to press
        """
        return self.run_cec_ctl(['--to', to.logical_address, '--user-control-pressed', 'ui-cmd={}'.format(button.value['str'])])


    def send_button_release(self, to: CECDevice) -> CompletedProcess:
        """
            Send a CEC command emulating a user releasing the last pressed button

            :param to: The CECDevice to send the button release to
        """
        return self.run_cec_ctl(['--to', to.logical_address, '--user-control-released'])
    

    def send_volume_up(self, to: CECDevice) -> None:
        """
            Send a CEC signal to emulate the volume-up button beeing pressed, then released

            :param to: Target CECDevice
        """
        self.send_button_press(to=to, button=CECButton.VOLUME_UP)
        self.send_button_release(to=to)
        return
    

    def send_volume_down(self, to: CECDevice) -> None:
        """
            Send a CEC signal to emulate the volume-down button beeing pressed, then released

            :param to: Target CECDevice
        """
        self.send_button_press(to=to, button=CECButton.VOLUME_DOWN)
        self.send_button_release(to=to)
        return
    

    def ask_power_status(self, to: CECDevice) -> str:
        """
            Send a CEC signal to ask a device to report his power status

            :param to: The target CECDevice
            :return: a string indicating the device power status among ('on', 'standby', 'to-on', 'to-standby')
        """
        result = self.run_cec_ctl(['--to', to.logical_address, '--give-device-power-status'])
        result.check_returncode()

        match = re.match(self.REGEX_RESPONSE_PWR_STATE, result.stdout)
        if not match:
            raise Exception('Cannot find power status in ask_power_status response')
        
        return match.group(1)
    

    def send_power_off(self, to: CECDevice) -> CompletedProcess:
        """
            Send a CEC signal to put target device in standby mode
            standby is a low energy mode (almost like power off) letting device respond to HDMI-CEC command

            If you want a real turn off, you should consider using send_button_press with button power off instead
            device behavior might vary

            :param to: The CECDevice to put in standby mode
        """
        return self.run_cec_ctl(['--to', to.logical_address, '--standby'])


    def send_power_on(self, to: CECDevice) -> CompletedProcess:
        """
            Send a CEC signal to power on target device and try to acquire signal
            this is technically the 'image view on' command.

            If you want a real turn on, you should consider using send_button_press with button power on instead
            device behavior might vary

            :param to: The CECDevice to power on
        """
        return self.run_cec_ctl(['--to', to.logical_address, '--image-view-on'])
    
    
    def broadcast_active_source(self) -> CompletedProcess:
        """
            Broadcast a CEC signal to indicate this device started transmitting a stream

            Behavior might vary, some device will automatically select the new active source as image input
            some will simply ignore it

            I you want a more reliable way to select video input, you should consider using send_button_press with 
            input select button
        """
        return self.run_cec_ctl(['--active-source', 'phys-addr={}'.format(self.physical_address)])
    

    def broadcast_inactive_source(self) -> CompletedProcess:
        """
            Broadcast a CEC signal to indicate this device stopped transmitting a stream

            Behavior might vary, some device will automatically fallback to other source as image input
            some will simply ignore it

            I you want a more reliable way to select video input, you should consider using send_button_press with 
            input select button
        """
        return self.run_cec_ctl(['--inactive-source', 'phys-addr={}'.format(self.physical_address)])
    

    def broadcast_request_active_source(self) -> list:
        """
            Broadcast a CEC signal to ask every devices to report if he is an active source
             
            Behavior might be quite erratic depending on how well devices adhere to CEC norms.
            That mean you could very well have an active source, yet having no response in request_active_source.

            :raise: Raise exception if command fail or timeout
            :return: A list of active sources physical addresses as strings
        """
        result = self.run_cec_ctl(['--request-active-source'])
        result.check_returncode()
        if re.match(self.REGEX_RESPONSE_TIMEOUT, result.stdout):
            raise ResponseTimeoutException('Timeout when requesting active source. Either no active source, or device loosely follow CEC standard.')
        
        active_sources = []
        active_source = None
        for line in result.stdout.splitlines():
            match = re.match(self.REGEX_RESPONSE_FROM, line)
            if match :
                if active_source != None:
                    active_sources.append(active_source)

                active_source = {'logical_address': match.group(1), 'physical_address': None}                    

            match = re.match(self.REGEX_RESPONSE_PHYSICAL_ADDRESS, line)
            if match :
                active_source['physical_address'] = match.group(1)

        if active_source != None :
            active_sources.append(active_source)

        return active_sources