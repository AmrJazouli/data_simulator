import vcgencmd
import subprocess
from datetime import datetime
import uuid


class Raspberry(object):
    """
        This class defines a Raspberry Pi object with its attributes in order to monitor its health
    """

    def __init__(self):
        """
            This function creates a new raspberry pi instance if it doesn't exist yet
        """

        my_cmd = vcgencmd.Vcgencmd()

        self._uuid = str(uuid.uuid4())  # Generates a random and secured UUID.
        self._device = "raspberry"
        self._gpu_temp_celsius = my_cmd.measure_temp()

        cpu = subprocess.Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'],
                               stdout=subprocess.PIPE).communicate()[0]
        self._cpu_temp_celsius = (int(cpu) / 1000)
        self._frequency_arm_hz = my_cmd.measure_clock('arm')
        self._frequency_core_hz = my_cmd.measure_clock('core')
        self._frequency_pwm_hz = my_cmd.measure_clock('pwm')
        self._voltage_core_v = my_cmd.measure_volts('core')
        self._voltage_sdram_c_v = my_cmd.measure_volts('sdram_c')
        self._voltage_sdram_i_v = my_cmd.measure_volts('sdram_i')
        self._voltage_sdram_p_v = my_cmd.measure_volts('sdram_p')
        self._memory_arm_bytes = my_cmd.get_mem('arm')
        self._memory_gpu_bytes = my_cmd.get_mem('gpu')

        throttled_out = subprocess.Popen(['vcgencmd', 'get_throttled'], stdout=subprocess.PIPE).communicate()
        throttled_value = throttled_out[0].decode().split('=')[1]
        self._throttled = throttled_value.split('\n')[0]

    # --- GETTERS [NO SETTERS - DATA CANNOT BE MODIFIED] ---#
    @property
    def uuid(self):
        """
            This property represent the UUID of the raspberry
        :return: uuid value
        """
        return self._uuid

    @property
    def device(self):
        """
            This property represents the device name
        :return: device name
        """
        return self._device

    @property
    def gpu_temp_celsius(self):
        """
            This property represent the measurement of GPU temperature of the device in ºC
        :return: GPU temperature measurement
        """
        return self._gpu_temp_celsius

    @property
    def cpu_temp_celsius(self):
        """
            This property represent the measurement of CPU temperature of the device in ºC
        :return: CPU temperature measurement
        """
        return self._cpu_temp_celsius

    @property
    def frequency_arm_hz(self):
        """
            This property represents the measurement of ARM frequency in Hz
        :return: ARM frequency measurement
        """
        return self._frequency_arm_hz

    @property
    def frequency_core_hz(self):
        """
            This property represents the measurement of Core frequency in Hz
        :return: Core frequency measurement
        """
        return self._frequency_core_hz

    @property
    def frequency_pwm_hz(self):
        """
            This property represents the measurement of Power frequency in Hz
        :return: Power frequency measurement
        """
        return self._frequency_pwm_hz

    @property
    def voltage_core_v(self):
        """
            This property represents the measurement of Core Voltage in Volts
        :return: Core Voltage measurement
        """
        return self._voltage_core_v

    @property
    def voltage_sdram_c_v(self):
        """
            This property represents the measurement of SDRAM C V Voltage in Volts
        :return: SDRAM C V Voltage measurement
        """
        return self._voltage_sdram_c_v

    @property
    def voltage_sdram_i_v(self):
        """
            This property represents the measurement of SDRAM I V Voltage in Volts
        :return: SDRAM I V Voltage measurement
        """
        return self._voltage_sdram_i_v

    @property
    def voltage_sdram_p_v(self):
        """
            This property represents the measurement of SDRAM P V Voltage in Volts
        :return: SDRAM P V Voltage measurement
        """
        return self._voltage_sdram_p_v

    @property
    def memory_arm_bytes(self):
        """
            This property represents the measurement of ARM Bytes memory
        :return: ARM Bytes memory measurement
        """
        return self._memory_arm_bytes

    @property
    def memory_gpu_bytes(self):
        """
            This property represents the measurement of GPU Bytes memory
        :return: GPU Bytes memory measurement
        """
        return self._memory_gpu_bytes

    @property
    def throttled(self):
        """
            This property represents the measurement of throttling
        :return: throttling measurement
        """
        return self._throttled

    @property
    def json(self):
        """
            This function returns a json document with all the raspberry pi information
        :return: json document
        """
        return {
            "uuid": self.uuid,
            "device": self.device,
            "loading_datetime": datetime.today().strftime('%Y-%m-%d@%H:%M:%S'),
            "GPU_temp_celsius": self.gpu_temp_celsius,
            "CPU_temp_celsius": self.cpu_temp_celsius,
            "frequency_arm_hz": self.frequency_arm_hz,
            "frequency_core_hz": self.frequency_core_hz,
            "frequency_pwm_hz": self.frequency_pwm_hz,
            "voltage_core_v": self.voltage_core_v,
            "voltage_sdram_c_v": self.voltage_sdram_c_v,
            "voltage_sdram_i_v": self.voltage_sdram_i_v,
            "voltage_sdram_p_v": self.voltage_sdram_p_v,
            "memory_arm_bytes": self.memory_arm_bytes,
            "memory_gpu_bytes": self.memory_gpu_bytes,
            "throttled": self.throttled
        }

    def __str__(self):
        return str(self.json)
