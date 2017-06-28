# Python RGB Keyboards, Copyright (C) 2017 by RedFantom
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
import platform
from cue_sdk.api import *
from cue_sdk.structures import *
from cue_sdk.enumerations import *
from cue_sdk.exceptions import *
from pynput import keyboard as kb
from .keys import *


class Corsair(object):
    """
    This class provides a wrapper around the Corsair CUE SDK that is provided freely to everyone as described in
    README.md of the corsair folder in this repository.
    """

    def __init__(self, sdk_dir=os.path.join(os.path.dirname(os.path.realpath(__file__)).replace("corsair", ""), "sdk")):
        if int(platform.architecture()[0][:2]) == 64:
            self.library = CUESDK(os.path.join(sdk_dir, "Corsair64.dll"))
        else:
            self.library = CUESDK(os.path.join(sdk_dir, "Corsair.dll"))
        self._callback = None
        self._listener = None

    @staticmethod
    def get_brand():
        """
        Returns the brand of the keyboard in use for the universal classes
        :return: string of brand
        """
        return "corsair"

    def get_version(self):
        """
        Returns the version of the SDK that is loaded, does require a keyboard to be set up
        :return: str version
        """
        return self.library.perform_protocol_handshake().sdk_ver

    def get_layout(self):
        """
        Return the int number that corresponds to the physical layout of the keyboard
        :return: int corresponding to layout
        """
        results = None
        for i in range(0, self.library.get_device_count()):
            if self.library.get_device_info(i).type == 2:
                results = self.library.get_device_info()
                break
        if not results:
            raise ValueError("Could not detect a Corsair keyboard")
        return results.physicalLayout

    def get_device_available(self):
        """
        Return availability of the keyboard to the user, using the protocol handshake function
        :return: bool True if available, False if not
        """
        return bool(self.library.get_device_info())

    @staticmethod
    def set_control_device(device_type=0):
        """
        Function not required for Corsair keyboards
        :param device_type: int device type
        :return: True
        """
        return True

    def set_led_control_enabled(self, enable=True):
        """
        Function to take control of the keyboard. Requests exclusive control if enable is True, releases exclusive
        control if enable is False.
        :param enable: if True requests control, if False releases control
        :return: True if successful
        """
        if not isinstance(enable, bool):
            raise ValueError("Parameter enable is not bool type")
        if enable:
            return self.library.request_control(CAM.ExclusiveLightingControl)
        else:
            return self.library.release_control(CAM.ExclusiveLightingControl)

    def set_led_effect(self, effect):
        """
        Sets a LED effect on the Corsair keyboard
        :param effect: int that identifies effect
        :return: True if successful
        """
        raise NotImplementedError("LED Effects have not yet been implemented for Corsair keyboards")

    def set_full_led_color(self, r, g, b):
        """
        Set the color of the whole keyboard
        :param r: int, 0 to 255
        :param g: int, 0 to 255
        :param b: int, 0 to 255
        :return: True if successful
        """
        if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
            raise ValueError("Parameters passed not all int type")
        if not 0 < r < 255 or not 0 < g < 255 or not 0 < b < 255:
            raise ValueError("Parameters not within range")
        return self.library.set_led_colors([CorsairLedColor(i, r, g, b) for i in keys.values()])

    def set_ind_led_color(self, leds):
        """
        Sets the colors of individual LEDs by keyname
        :param leds: dictionary with keynames as key and tuples (r, g, b) as values
        :return:
        """
        if not isinstance(leds, dict):
            raise ValueError("Parameter leds is not a dictionary")
        parameter = []
        for key, value in leds.items():
            if key not in keys:
                raise ValueError("Invalid key found")
            if not isinstance(value, tuple):
                raise ValueError("Value found for key not tuple")
            if not len(value) == 3:
                raise ValueError("Value found for key not with length 3")
            if not keys[key]:
                continue
            (r, g, b) = value
            parameter.append(CorsairLedColor(keys[key], r, g, b))
        return self.library.set_led_colors(parameter)

    def set_key_callback(self, callback):
        """
        Set the callback for when a key is pressed
        :param callback: callable object to be called upon keypress with parameters
        :return: None
        """
        if not callable(callback):
            raise ValueError("Parameter callback passed not callable")
        self._callback = callback
        self._listener = kb.Listener(on_press=self._callback)

    def enable_key_callback(self, enable=True):
        """
        Enables the key callback set with set_key_callback
        :param enable: enables if True, disables if False
        :return: None
        """
        if not self._callback or not callable(self._callback):
            raise ValueError("Callback not set. Please use set_key_callback")
        if not self._listener or not isinstance(self._listener, kb.Listener):
            raise ValueError("Callback set but listener not found")
        if enable:
            self._listener.start()
        else:
            self._listener.stop()
            while self._listener.is_alive():
                pass
            return

    """
    The following functions are brand specific and might not be available on all keyboards. Please only use these
    functions if your are targeting a specific brand or keyboard. You can do this by letting the user enter their
    keyboard and changing the functions you call based upon that.
    """
    def get_led_positions(self):
        return self.library.get_led_positions()

    def get_led_by_name(self, keyname):
        return self.library.get_led_by_name(keyname)

    def perform_protocol_handshake(self):
        return self.library.perform_protocol_handshake()

