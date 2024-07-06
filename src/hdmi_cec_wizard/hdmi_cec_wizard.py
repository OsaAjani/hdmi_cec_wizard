import subprocess
from subprocess import CompletedProcess
import re
import shlex
import glob
from .cec_device import CECDevice, LocalCECDevice, DeviceTypes
import shutil
import signal
from .exceptions import FollowerStoppedException

class HDMICECWizard ():
    """
        This class allow for configuration and handling of HDMI-CEC devices
        through the cec-ctl cli tool by running command and parsing results

        :param cec_handle: The /dev/cecX to use with HDMICECWizard, can be null on init but must be set before init.
        :type device: string|None
    """

    # Regex for parsing results from cec-ctl
    REGEX_VERSION = r'CEC Version\s+:\s+(.+)'
    REGEX_PHYSICAL_ADDRESS = r'Physical Address\s+:\s+(\w+\.\w+\.\w+\.\w+)'
    REGEX_LOGICAL_ADDRESS = r'Logical Address\s+:\s+(\d+)\s+'
    REGEX_DEVICE_TYPE = r'Primary Device Type\s+:\s+(.+)'
    REGEX_VENDOR_ID = r'Vendor ID\s+:\s+(.+)'
    REGEX_POWER_STATUS = r'Power Status\s+:\s+(.+)'
    REGEX_OSD_NAME = r'OSD Name\s+:\s+\'(.+)\''

    REGEX_TOPO_DEVICE_DELIMITER = r'^\s+System Information for device (\d+) \(\w+\) from device (\d+) \(.+\):'
    REGEX_TOPO_LOGICAL_ADDRESS = r'^\s+System Information for device (\d+) (.+):'
    REGEX_TOPO_TOPO_DELIMITER = r'^\s+Topology:\s*'
    REGEX_TOPO_TOPO_DEVICE_PHYSICAL_ADDRESS = r'^(\s+)(\w+\.\w+\.\w+\.\w+):\s*'


    def __init__(self, cec_handle: str = None) -> None:
        # /dev/cecX handle for our Local CEC device to use with cec-ctl  
        self.cec_handle = cec_handle

        # This is the handle to our cec-follower process, required by some HDMI device
        # to work as expected
        self.follower_handle = None

        # Our Local CEC device to interract with the rest of the world
        # will be initialized by calling self.start_follower or with self.init_cec
        self.local_device: LocalCECDevice = None
        
        # All connected devices
        self.connected_devices: list[CECDevice] = None

        # The main screen to be used to show images
        self.main_screen: CECDevice = None


    def __on_follower_exit(self, signum: int, frame) -> None :
        """
            This function will be call when a cec-follower have be started and we have received SIGCHLD signal
            indicating that it stopped.

            :raise FollowerStoppedException: This will raise an error when the cec-follower stop, allowing the user
                to choose what to do with this information
        """
        if signum == signal.SIGCHLD:
            # Get the process result, this should be immediate as the process is supposed to be stopped
            process_result = self.follower_handle.wait() 

            # Empty the follower handle
            self.follower_handle = None 

            raise FollowerStoppedException("cec-follower has stopped", process_result)


    def __run_cec_ctl_cmd(self, command_args: list) -> CompletedProcess:
        """
            Run a cec-ctl command and return result
            :param command_args: Parameters to pass to cec-ctl command. 
                all args will be escaped with shlex.join
            :type command_args: array
        """
        command = shlex.join(['cec-ctl'] + command_args)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result
    

    def __parse_device_infos(self, raw: str, is_topo: False) -> dict : 
        """
            Try to extract device infos from a cec-ctl driver/topology string

            :param raw: The string to parse
            :param is_topo: Default to False, pass to True if the raw data come from a show topology command
        """
        cec_params = {}
        match = re.search(self.REGEX_VERSION, raw)
        if not match :
            raise Exception('Cannot find the CEC Version')
        cec_params['cec_version'] = match.group(1)

        match = re.search(self.REGEX_PHYSICAL_ADDRESS, raw)
        if not match :
            raise Exception('Cannot find the Physical Address')
        cec_params['physical_address'] = match.group(1)

        if is_topo :
            match = re.search(self.REGEX_TOPO_LOGICAL_ADDRESS, raw)
        else :
            match = re.search(self.REGEX_LOGICAL_ADDRESS, raw)
        if not match :
            raise Exception('Cannot find the Logical Address')
        cec_params['logical_address'] = match.group(1)

        match = re.search(self.REGEX_DEVICE_TYPE, raw)
        if not match :
            raise Exception('Cannot find the Device Type')
        
        found = False
        for device_type in DeviceTypes :
            if match.group(1) == device_type.value['str']:
                cec_params['device_type'] = device_type
                found = True
                break
        
        if not found :
            raise Exception('Invalid Device Type')
        
        match = re.search(self.REGEX_VENDOR_ID, raw)
        if not match :
            raise Exception('Cannot find the Vendor ID')
        cec_params['vendor_id'] = match.group(1)

        match = re.search(self.REGEX_POWER_STATUS, raw)
        if not match :
            raise Exception('Cannot find the Power Status')
        cec_params['power_status'] = match.group(1)

        match = re.search(self.REGEX_OSD_NAME, raw)
        if match:
            cec_params['osd_name'] = match.group(1)

        return cec_params
    

    def autoconfig(self, device_type: DeviceTypes = None, osd_name: str = None) -> None:
        """
            This method will autoconfig the HDMI-CEC Wizard, trying to automatically :
                - Detect the /dev/cecX to use and set it
                - Initialize the CEC Local Device
                - Populate the connected devices list
                - Select the main screen among connected device if available

            :param device_type: The device type to configure our CEC device as. Must be one of DeviceTypes or None to default to Playback
            :param osd_name: The OSD Name to use for our device (max 14 chars), if None cec-ctl will use device type instead

            :raise: This method will raise exception if any step fail
        """
        if not self.cec_handle :
            self.cec_handle = self.autodetect_cec_handle()
        
        self.init_cec(device_type=device_type, osd_name=osd_name)
        self.connected_devices = self.list_connected_devices()
        self.main_screen = self.autodetect_main_screen()
    

    def set_cec_handle(self, cec_handle: str) -> None:
        """
            Update the /dev/cecX device to use 
        """
        self.cec_handle = cec_handle


    def autodetect_cec_handle(self) -> str:
        """
            Try to autodetect the /dev/cecX port to use by checking which HDMI port is connected
            the autodectect only works if one and only one HDMI port is connected to a device.
            If no HDMI port is connected it will fail, same is true if more than one port is connected
            :return: The /dev/cecX to use if autodetect succeded
            :raise: Raise exception if autodetect fail
        """

        connected_devices = []

        cec_handles = glob.glob('/dev/cec*')
        for cec_handle in cec_handles :
            result = self.__run_cec_ctl_cmd(['-d', cec_handle])
            result.check_returncode()

            match = re.search(self.REGEX_PHYSICAL_ADDRESS, result.stdout)
            if not match :
                continue

            physical_address = match.group(1)

            # A physical address of f.f.f.f mean the the device is not connected
            if physical_address == 'f.f.f.f' :
                continue

            connected_devices.append(cec_handle)

        if len(connected_devices) != 1:
            raise Exception('Cannot autodetect device. {} device(s) found.'.format(len(connected_devices)))
        
        return connected_devices[0]


    def start_follower(self) -> None:
        """
            Start a cec-follower process in background with the /dev/cecX set in self.device_handle
            This is required in order for our device to respond to pool requests by other equipements in the 
            HDMI-CEC network.

            Some functionnalities of HDMI may be instable / not work at all without the cec-follower answering their
            commands

            Start follower will try to only start cec-follower once by looking at self.follower_handle

            :raise: Start follower dont raise exception by himself, but when the cec-follower stop, 
                the exception FollowerStoppedException will be triggered by __on_follower_exit()
        """
        if not self.follower_handle :
            bin_path = shutil.which('cec-follower')
            self.follower_handle = subprocess.Popen(shlex.join(bin_path, '-d', self.cec_handle), shell=True, 
                                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            # In UNIX when a child process stop, the parent receive a SIGCHLD signal
            # we use that to trigger the self.__on_follower_exit in turn raising the Exception
            signal.signal(signal.SIGCHLD, self.__on_follower_exit)


    def init_cec(self, device_type: DeviceTypes = None, osd_name: str = None) -> None:
        """
            Init the CEC device to make it a playback device, capable of talking with other HDMI connected devices.
            The function will also start the cec-follower in background 
            
            :param device_type: The device type to configure our CEC device as. Must be one of DeviceTypes or None to default to Playback
            :param osd_name: The OSD Name to use for our device (max 14 chars), if None cec-ctl will use device type instead

            :raise: Raise exception if initalizatoin fail
        """

        if not self.cec_handle :
            raise Exception('You must define the cec_handle on initialization or later with set_cec_handle() before init')

        if not device_type :
            device_type = DeviceTypes.PLAYBACK

        # Init our cec device
        command = ['-d', self.cec_handle, device_type.value['param']]
        if osd_name :
            if len(osd_name > 14) :
                raise Exception('OSD Name cannot exceed 14 characters.')
            command = command + ['--osd-name', osd_name]

        result = self.__run_cec_ctl_cmd(command)
        result.check_returncode()

        # Read info about this device and set self.local_device as a LocalCECDevice
        result = self.__run_cec_ctl_cmd(['-d', self.cec_handle])
        result.check_returncode()

        # Init our CEC device with params parsed from cec-ctl response
        device_params = self.__parse_device_infos(result.stdout)
        device_params['cec_handle'] = self.cec_handle
        self.local_device = LocalCECDevice(**device_params)

        # Now that the device is initialized, we must also start our cec-follower
        # this is required in order for our device to respond to pool request
        # by the other devices in the network
        self.start_follower()

        return


    def list_connected_devices(self) -> list:
        """
            List CEC devices connected to our local device 

            :raise: Raise exception if cannot list connected devices
            :return: Return a list of all the connected devices accessible through or local device
        """
        result = self.local_device.run_cec_ctl(['--show-topology'], skip_info=False)
        result.check_returncode()

        raws = []
        raw = []
        for line in result.stdout.splitlines():
            if re.match(self.REGEX_TOPO_DEVICE_DELIMITER, line):
                if len(raw) > 0:
                    raws.append(raw)
                    raw = []

            elif re.match(self.REGEX_TOPO_TOPO_DELIMITER, line):
                break

            raw.append(line)
        raws.append(raw)

        connected_devices = []
        for raw in raws:
            device_params = self.__parse_device_infos(raw, is_topo=True)
            connected_devices.append(CECDevice(**device_params))

        return connected_devices
    

    def autodetect_main_screen(self) -> CECDevice:
        """
            Try to find the main screen among the connected device
            For know we will consider the main screen is necessarily the one with physical address 0.0.0.0

            To work the self.connected_devices list must have been populated, either manually with list_connected_devices
            or automatically with self.autoconfig
        """
        for device in self.connected_devices:
            if device.physical_address == '0.0.0.0' :
                return device
    

    def get_topology(self) -> list:
        """
            Return the topology of the HDMI CEC devices connected to the system

            :raise: Raise exception if cannot list connected devices
            :return: Return a tree-like structure of physical addresses of all the connected devices, with parent and childs
        """
        result = self.local_device.run_cec_ctl(['--show-topology'])
        result.check_returncode()

        raw = []
        start = False
        for line in result.stdout.splitlines():
            if re.match(self.REGEX_TOPO_TOPO_DELIMITER, line):
                start = True

            if not start :
                continue
            
            raw.append(line)

        topology = []
        parent_device = None
        previous_device_spaces_len = None
        for line in raw :
            if re.match(self.REGEX_TOPO_TOPO_DELIMITER, line):
                continue
            
            # For each line try to extract the device physical address and leading spaces
            match = re.match(self.REGEX_TOPO_TOPO_DEVICE_PHYSICAL_ADDRESS, line)
            if not match:
                continue

            # Leading spaces length help us to find the topo
            spaces_len = len(match.group(1))

            # First device is always the root
            if not previous_device_spaces_len :
                parent_device = {
                    'physical_address': match.group(2),
                    'childs': [],
                    'parent': None,
                }
                topology.append(parent_device)

                previous_device_spaces_len = len(match.group(1))
                continue

            # We know a device is a child of the previous one if leading spaces is larger
            if spaces_len > previous_device_spaces_len:
                new_device = {
                    'physical_address': match.group(2),
                    'childs': [],
                    'parent': parent_device,
                }

                parent_device['childs'].append(new_device)
                parent_device = new_device

            # If same length they share the same parent
            elif spaces_len == previous_device_spaces_len :
                new_device = {
                    'physical_address': match.group(2),
                    'childs': [],
                    'parent': parent_device,
                }

                parent_device['childs'].append(new_device)

            # If shorter, it belongs to the device parent
            else :                   
                    new_device = {
                        'physical_address': match.group(2),
                        'childs': [],
                        'parent': parent_device['parent'],
                    }

                    if parent_device['parent'] == None :
                        topology.append(new_device)
                    else :
                        parent_device['parent']['childs'].append(new_device)

                    parent_device = new_device

        return topology

        



