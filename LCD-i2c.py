#!/usr/bin/python
"""
LCD-i2c.py
    Python module to write to simple character screens with an i2c backpack.

This program uses (modified) parts of lcd_i2c.py by Matt Hawkins, licensed under the
GNU GPL v3 or at your option any later version.

Copyright 2016 Tijndagamer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import smbus
from time import sleep

class LCD_i2c:

    bus = smbus.SMBus(1)
    address = None
    lcd_width = None
    lcd_max_lines = None
    lcd_backlight = None

    LCD_CHR = 1 # Mode - Sending data
    LCD_CMD = 0 # Mode - Sending command

    # Memory addresses for the lines
    LCD_LINE_1_ADDRESS = 0x80
    LCD_LINE_2_ADDRESS = 0xC0
    LCD_LINE_3_ADDRESS = 0x94
    LCD_LINE_4_ADDRESS = 0xD4

    LCD_BACKLIGHT_ON = 0x08
    LCD_BACKLIGHT_OFF = 0x00

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    def __init__(self, address = 0x27, lcd_width = 16, lcd_max_lines = 2, lcd_backlight = True):
        self.address = address
        self.lcd_width = lcd_width
        self.lcd_max_lines = lcd_max_lines
        if lcd_backlight:
            self.lcd_backlight = LCD_BACKLIGHT_ON
        else:
            self.lcd_backlight = LCD_BACKLIGHT_OFF

        # Initialise display
        lcd_write_byte(0x33, self.LCD_CMD) # 110011 Initialise
        lcd_write_byte(0x32, self.LCD_CMD) # 110010 Initialise
        lcd_write_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
        lcd_write_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        lcd_write_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
        lcd_write_byte(0x01, self.LCD_CMD) # 000001 Clear display
        sleep(self.E_DELAY)

    def lcd_toggle_enable(self, byte):
        """Enables toggle."""
        sleep(self.E_DELAY)
        self.bus.write_byte(self.address, (bits | self.ENABLE))
        sleep(self.E_PULSE)
        self.bus.write_byte(self.address,(bits & ~self.ENABLE))
        sleep(self.E_DELAY)

    def lcd_write_byte(self, byte, mode):
        """Send one byte of data to the i2c backpack.

        byte: the data to send
        mode: sending data or a command. 1 for data, 0 for a command.
        """

        byte_high = mode | (byte & 0xF0) | self.lcd_backlight
        byte_low = mode | (byte << 4) & 0xF0 | self.lcd_backlight

        self.bus.write_byte(self.address, byte_high)
        self.lcd_toggle_enable(byte_high)

        self.bus.write_byte(self.address, byte_low)
        self.lcd_toggle_enable(byte_low)

    def lcd_print(self, string, line):
        """Sends a string to display on the LCD.

        string: the string to be printed
        line: the line on which it will be printed
        """

        string = string.ljust(self.LCD_WIDTH, " ")

        # Tell where in the memory the string has to be written to
        line_addressess = self.LCD_LINE_1_ADDRESS
        if line == 1:
            line_address = self.LCD_LINE_1_ADDRESS
        elif line == 2:
            line_address = self.LCD_LINE_2_ADDRESS
        elif line == 3:
            line_address = self.LCD_LINE_3_ADDRESS
        elif line == 4:
            line_address = self.LCD_LINE_4_ADDRESS
        self.lcd_write_byte(line_address, self.LCD_CMD)

        for i in range(LCD_WIDTH): # Extra characters will be ignored.
            self.lcd_write_byte(ord(string[i]), self.LCD_CHR)
