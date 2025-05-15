"""
Modified version of RPI-PICO-I2C-LCD by Tyler Peppy
Original repository: https://github.com/T-622/RPI-PICO-I2C-LCD

This version has been modified by KuoKuo in 2025 to support Raspberry Pi Zero.
The modified version is part of the ZeroBETH project:
https://github.com/206cc/ZeroBETH

The original MIT License is retained below.

MIT License

Copyright (c) 2023 Tyler Peppy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import time
from smbus2 import SMBus
from lib.lcd_api import LcdApi

# PCF8574 pin definitions
MASK_RS = 0x01       # P0
MASK_RW = 0x02       # P1
MASK_E  = 0x04       # P2

SHIFT_BACKLIGHT = 3  # P3
SHIFT_DATA      = 4  # P4-P7

class I2cLcd(LcdApi):
    # Implements a HD44780 character LCD connected via PCF8574 on I2C

    def __init__(self, i2c_bus, i2c_addr, num_lines, num_columns):
        self.i2c = SMBus(i2c_bus)
        self.i2c_addr = i2c_addr
        self._write_byte(0)
        time.sleep(0.02)  # Allow LCD time to power up

        # Send reset 3 times
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.005)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)

        # Put LCD into 4-bit mode
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        time.sleep(0.001)

        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def _write_byte(self, value):
        self.i2c.write_byte(self.i2c_addr, value)

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        self._write_byte(byte | MASK_E)
        self._write_byte(byte)

    def hal_backlight_on(self):
        self._write_byte(1 << SHIFT_BACKLIGHT)

    def hal_backlight_off(self):
        self._write_byte(0)

    def hal_write_command(self, cmd):
        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                (((cmd >> 4) & 0x0F) << SHIFT_DATA))
        self._write_byte(byte | MASK_E)
        self._write_byte(byte)

        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                ((cmd & 0x0F) << SHIFT_DATA))
        self._write_byte(byte | MASK_E)
        self._write_byte(byte)

        if cmd <= 3:
            time.sleep(0.005)

    def hal_write_data(self, data):
        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                (((data >> 4) & 0x0F) << SHIFT_DATA))
        self._write_byte(byte | MASK_E)
        self._write_byte(byte)

        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                ((data & 0x0F) << SHIFT_DATA))
        self._write_byte(byte | MASK_E)
        self._write_byte(byte)
