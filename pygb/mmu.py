#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from pygb.io_registers import IO_Registers

class MMU:

    def __init__(self, rom):
        self.boot_rom = [
        0x31, 0xFE, 0xFF, 0xAF, 0x21, 0xFF, 0x9F, 0x32, 0xCB, 0x7C, 0x20, 0xFB,
        0x21, 0x26, 0xFF, 0x0E, 0x11, 0x3E, 0x80, 0x32, 0xE2, 0x0C, 0x3E, 0xF3,
        0xE2, 0x32, 0x3E, 0x77, 0x77, 0x3E, 0xFC, 0xE0, 0x47, 0x11, 0x04, 0x01,
        0x21, 0x10, 0x80, 0x1A, 0xCD, 0x95, 0x00, 0xCD, 0x96, 0x00, 0x13, 0x7B,
        0xFE, 0x34, 0x20, 0xF3, 0x11, 0xD8, 0x00, 0x06, 0x08, 0x1A, 0x13, 0x22,
        0x23, 0x05, 0x20, 0xF9, 0x3E, 0x19, 0xEA, 0x10, 0x99, 0x21, 0x2F, 0x99,
        0x0E, 0x0C, 0x3D, 0x28, 0x08, 0x32, 0x0D, 0x20, 0xF9, 0x2E, 0x0F, 0x18,
        0xF3, 0x67, 0x3E, 0x64, 0x57, 0xE0, 0x42, 0x3E, 0x91, 0xE0, 0x40, 0x04,
        0x1E, 0x02, 0x0E, 0x0C, 0xF0, 0x44, 0xFE, 0x90, 0x20, 0xFA, 0x0D, 0x20,
        0xF7, 0x1D, 0x20, 0xF2, 0x0E, 0x13, 0x24, 0x7C, 0x1E, 0x83, 0xFE, 0x62,
        0x28, 0x06, 0x1E, 0xC1, 0xFE, 0x64, 0x20, 0x06, 0x7B, 0xE2, 0x0C, 0x3E,
        0x87, 0xF2, 0xF0, 0x42, 0x90, 0xE0, 0x42, 0x15, 0x20, 0xD2, 0x05, 0x20,
        0x4F, 0x16, 0x20, 0x18, 0xCB, 0x4F, 0x06, 0x04, 0xC5, 0xCB, 0x11, 0x17,
        0xC1, 0xCB, 0x11, 0x17, 0x05, 0x20, 0xF5, 0x22, 0x23, 0x22, 0x23, 0xC9,
        0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83,
        0x00, 0x0C, 0x00, 0x0D, 0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
        0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99, 0xBB, 0xBB, 0x67, 0x63,
        0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
        0x3c, 0x42, 0xB9, 0xA5, 0xB9, 0xA5, 0x42, 0x4C, 0x21, 0x04, 0x01, 0x11,
        0xA8, 0x00, 0x1A, 0x13, 0xBE, 0x20, 0xFE, 0x23, 0x7D, 0xFE, 0x34, 0x20,
        0xF5, 0x06, 0x19, 0x78, 0x86, 0x23, 0x05, 0x20, 0xFB, 0x86, 0x20, 0xFE,
        0x3E, 0x01, 0xE0, 0x50
        ]
        self.rom = rom
        self.video_ram = [0x00]*0x2000
        self.internal_ram = [0x00]*0x2000
        self.oam = [0x00]*0xa0
        self.something = [0x00]*0x60
        self.io_ports = [0x00]*0x4c
        self.high_internal_ram = [0x00]*0x80
        self.bootstrap_enabled = True
        
    def read_byte(self, address):
        if ( address < 0x100 ) and self.bootstrap_enabled:
            return self.boot_rom[address]
        if address < 0x8000:
            return self.rom.read_rom_byte(address)
        if address < 0xa000:
            return self.video_ram[address - 0x8000]
        if address < 0xc000:
            return self.rom.read_external_ram_byte(address)
        if address < 0xe000:
            return self.internal_ram[address - 0xc000]
        if address < 0xfe00:
            return self.internal_ram[address - 0xe000] #Shadow
        if address < 0xfea0:
            return self.oam[address - 0xfe00]
        if address < 0xff00:
            return self.something[address - 0xfea0]
        if address < 0xff4c:
            return self.io_ports[address - 0xff00]
        if address < 0xff80:
            return 0x00 # Empty area
        if address < 0x10000:
            return self.internal_ram[address - 0xff80]

    def write_byte(self, address, value, hardware_operation = False):
        value = value & 0xff
        if address < 0x8000:
            self.rom.write_rom_byte(address, value)
        elif address < 0xa000:
            self.video_ram[address - 0x8000] = value
        elif address < 0xc000:
            self.rom.write_external_ram_byte(address, value)
        elif address < 0xe000:
            self.internal_ram[address - 0xc000] = value
        elif address < 0xfe00:
            self.internal_ram[address - 0xe000] = value # Shadow
        elif address < 0xfea0:
            self.oam[address - 0xfe00] = value
        elif address < 0xff00:
            self.something[address - 0xfea0] = value
        elif address < 0xff4c:
            if not hardware_operation:
                if address == IO_Registers.P1:
                    self.io_ports[address - 0xff00] = value | 0xf
                elif address == IO_Registers.DIV: # Reset div register
                    self.io_ports[address - 0xff00] = 0x00
                elif address == IO_Registers.DMA: # Start dma transfer
                    self.dma_transfer(value)
                else:
                    self.io_ports[address - 0xff00] = value
            else:     
                self.io_ports[address - 0xff00] = value
        elif address < 0x10000:
            if address == 0xff50:
                self.bootstrap_enabled = False
            else:
                self.internal_ram[address - 0xff80] = value

    def dma_transfer(self, start):
        address = start << 8
        if address >= 0x8000 and address < 0xE000:
            for i in range(0,0x9f):
                self.write_byte((0xFE00 + i), self.read_byte(address + 1))

    def read_word(self, address):
        return self.read_byte(address) | (self.read_byte(address + 1) << 8)

    def write_word(self, address, value):
        print(address)
        print(value)

        value = (value & 0xffff)
        self.write_byte(address, (value & 0xff))
        self.write_byte((address + 1), (value >> 8))