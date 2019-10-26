#!/usr/bin/env python3

import ctypes
import time
import sys

# https://stackoverflow.com/questions/11906925/python-simulate-keydown
# http://stackoverflow.com/questions/11906925/python-simulate-keydown

class MYINPUTSIM:

    LONG = ctypes.c_long
    DWORD = ctypes.c_ulong
    ULONG_PTR = ctypes.POINTER(DWORD)
    WORD = ctypes.c_ushort

    INPUT_MOUSE = 0
    INPUT_KEYBOARD = 1
    INPUT_HARDWARE = 2

    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_UNICODE = 0x0004

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = (('dx', MYINPUTSIM.LONG),
                ('dy', MYINPUTSIM.LONG),
                ('mouseData', MYINPUTSIM.DWORD),
                ('dwFlags', MYINPUTSIM.DWORD),
                ('time', MYINPUTSIM.DWORD),
                ('dwExtraInfo', MYINPUTSIM.ULONG_PTR))


    class KEYBDINPUT(ctypes.Structure):
        _fields_ = (('wVk', MYINPUTSIM.WORD),
                ('wScan', MYINPUTSIM.WORD),
                ('dwFlags', MYINPUTSIM.DWORD),
                ('time', MYINPUTSIM.DWORD),
                ('dwExtraInfo', MYINPUTSIM.ULONG_PTR))


    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = (('uMsg', MYINPUTSIM.DWORD),
                ('wParamL', MYINPUTSIM.WORD),
                ('wParamH', MYINPUTSIM.WORD))


    class _INPUTunion(ctypes.Union):
        INPUT_MOUSE = 0
        INPUT_KEYBOARD = 1
        INPUT_HARDWARE = 2
        _fields_ = (('mi', MYINPUTSIM.MOUSEINPUT),
                ('ki', MYINPUTSIM.KEYBDINPUT),
                ('hi', MYINPUTSIM.HARDWAREINPUT))


    class INPUT(ctypes.Structure):
        _fields_ = (('type', MYINPUTSIM.DWORD),
                ('union', MYINPUTSIM._INPUTunion))


    def send_input(self, *inputs):
        nInputs = len(inputs)
        LPINPUT = MYINPUTSIM.INPUT * nInputs
        pInputs = LPINPUT(*inputs)
        cbSize = ctypes.c_int(ctypes.sizeof(MYINPUTSIM.INPUT))
        return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)


    def input_structure(self, structure):
        if isinstance(structure, MYINPUTSIM.MOUSEINPUT):
            return MYINPUTSIM.INPUT(MYINPUTSIM.INPUT_MOUSE, 
            MYINPUTSIM._INPUTunion(mi=structure))
        if isinstance(structure, MYINPUTSIM.KEYBDINPUT):
            return MYINPUTSIM.INPUT(MYINPUTSIM.INPUT_KEYBOARD, 
            MYINPUTSIM._INPUTunion(ki=structure))
        if isinstance(structure, MYINPUTSIM.HARDWAREINPUT):
            return MYINPUTSIM.INPUT(MYINPUTSIM.INPUT_HARDWARE, 
            MYINPUTSIM._INPUTunion(hi=structure))
        raise TypeError('Cannot create INPUT structure!')


    def keyboard_input(self, code, flags):
        return MYINPUTSIM.KEYBDINPUT(0, code, flags, 0, None)


    def keyboard_event(self, code, flags=KEYEVENTF_UNICODE):
        return self.input_structure(self.keyboard_input(code, flags))


    def _press(self, character):
        code = ord(character)
        self.send_input(self.keyboard_event(code))
        self.send_input(self.keyboard_event(code, MYINPUTSIM.KEYEVENTF_KEYUP))

    def MyInput(self, strInput):
        for char in strInput:
            self._press(char)
            time.sleep(0.5)