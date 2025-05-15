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

class LcdApi:
    # HD44780 LCD controller command set
    LCD_CLR             = 0x01
    LCD_HOME            = 0x02
    LCD_ENTRY_MODE      = 0x04
    LCD_ENTRY_INC       = 0x02
    LCD_ENTRY_SHIFT     = 0x01
    LCD_ON_CTRL         = 0x08
    LCD_ON_DISPLAY      = 0x04
    LCD_ON_CURSOR       = 0x02
    LCD_ON_BLINK        = 0x01
    LCD_MOVE            = 0x10
    LCD_MOVE_DISP       = 0x08
    LCD_MOVE_RIGHT      = 0x04
    LCD_FUNCTION        = 0x20
    LCD_FUNCTION_8BIT   = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_10DOTS = 0x04
    LCD_FUNCTION_RESET  = 0x30
    LCD_CGRAM           = 0x40
    LCD_DDRAM           = 0x80

    LCD_RS_CMD          = 0
    LCD_RS_DATA         = 1

    LCD_RW_WRITE        = 0
    LCD_RW_READ         = 1

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines if num_lines <= 4 else 4
        self.num_columns = num_columns if num_columns <= 40 else 40
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True
        self.display_off()
        self.backlight_on()
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        self.hide_cursor()
        self.display_on()

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        self.hal_write_command(self.LCD_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def hide_cursor(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY |
                               self.LCD_ON_CURSOR | self.LCD_ON_BLINK)

    def blink_cursor_off(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY |
                               self.LCD_ON_CURSOR)

    def display_on(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def display_off(self):
        self.hal_write_command(self.LCD_ON_CTRL)

    def backlight_on(self):
        self.backlight = True
        self.hal_backlight_on()

    def backlight_off(self):
        self.backlight = False
        self.hal_backlight_off()

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3F
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += self.num_columns
        self.hal_write_command(self.LCD_DDRAM | addr)

    def addr_cursor(self):
        return (self.cursor_x, self.cursor_y)

    def putchar(self, char):
        if char == '\n':
            if self.implied_newline:
                pass
            else:
                self.cursor_x = self.num_columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = (char != '\n')
        if self.cursor_y >= self.num_lines:
            self.cursor_y = 0
        self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        location &= 0x7
        self.hal_write_command(self.LCD_CGRAM | (location << 3))
        self.hal_sleep_us(40)
        for i in range(8):
            self.hal_write_data(charmap[i])
            self.hal_sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_backlight_on(self):
        pass

    def hal_backlight_off(self):
        pass

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError

    def hal_sleep_us(self, usecs):
        # 用 time.sleep 替代 MicroPython 的 sleep_us（秒 = 微秒 / 1_000_000）
        time.sleep(usecs / 1_000_000.0)
