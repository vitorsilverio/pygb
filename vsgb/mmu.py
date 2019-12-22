#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array

from vsgb.apu import APU
from vsgb.boot_rom import boot_rom, cgb_boot_rom
from vsgb.cgb_palette import CGB_Palette
from vsgb.input import Input
from vsgb.io_registers import IO_Registers
from vsgb.cartridge import CartridgeType

# General Memory Map
# Start End     Description                      Notes
# 0000  3FFF    16KB ROM bank 00                 From cartridge, usually a fixed bank
# 4000  7FFF    16KB ROM Bank 01~NN              From cartridge, switchable bank via MBC (if any)
# 8000  9FFF    8KB Video RAM (VRAM)             Only bank 0 in Non-CGB mode
#                                                Switchable bank 0/1 in CGB mode
# A000  BFFF    8KB External RAM                 In cartridge, switchable bank if any
# C000  CFFF    4KB Work RAM (WRAM) bank 0
# D000  DFFF    4KB Work RAM (WRAM) bank 1~N     Only bank 1 in Non-CGB mode
#                                                Switchable bank 1~7 in CGB mode
# E000  FDFF    Mirror of C000~DDFF (ECHO RAM) 	 Typically not used
# FE00  FE9F    Sprite attribute table (OAM)
# FEA0  FEFF    Not Usable
# FF00  FF7F    I/O Registers
# FF80  FFFE    High RAM (HRAM)
# FFFF  FFFF    Interrupts Enable Register (IE) 	
class MMU:

    def __init__(self, rom : CartridgeType, apu: APU, _input : Input, cgb_mode: bool):
        self.rom = rom
        self.apu = apu
        self.input = _input
        self.vram = array.array('B', [0xff]*0x4000)
        self.wram = array.array('B', [0xff]*0x8000)
        self.oam = array.array('B', [0xff]*0xa0)
        self.zero_page = array.array('B', [0xff]*0x7f)
        self.io_ports = array.array('B', [0x01]*0x80)
        self.hram = array.array('B', [0xff]*0x80)
        self.bootstrap_enabled = True
        self.unusable_memory_space = array.array('B', [0xff]*0x60)
        self.cgb_mode = cgb_mode
        self.cgb_palette = CGB_Palette()
        if self.cgb_mode:
            self.boot_rom  = cgb_boot_rom
        else:
            self.boot_rom  = boot_rom

    def set_dma(self, dma):
        self.dma = dma

    def set_hdma(self, hdma):
        self.hdma = hdma
        
    def read_byte(self, address: int) -> int:
        if 0 <= address < 0x8000:
            if self.bootstrap_enabled and ((0 <= address <= 0xff) or (0x0200 <= address <= 0x08ff)):
                return self.boot_rom[address] & 0xff
            return self.rom.read_rom_byte(address)
        if 0x8000 <= address < 0xa000:
            if self.cgb_mode:
                bank = self.read_byte(IO_Registers.VBK) & 0x1
                return self.vram[(address - 0x8000)+(0x2000 * bank)] & 0xff
            else:
                return self.vram[address - 0x8000] & 0xff
        if 0xa000 <= address < 0xc000:
            return self.rom.read_external_ram_byte(address) & 0xff
        if 0xc000 <= address < 0xe000:
            if self.cgb_mode:
                if 0xc000 <= address < 0xd000:
                    return self.wram[address - 0xc000] & 0xff
                bank = self.read_byte(IO_Registers.SVBK) & 0x7
                return self.wram[(address - 0xd000)+(bank*0x1000)] & 0xff
            else:
                return self.wram[address - 0xc000] & 0xff
        if 0xe000 <= address < 0xfe00:
            return self.read_byte(address - 0x2000) #Echo RAM
        if 0xfe00 <= address < 0xfea0:
            return self.oam[address - 0xfe00] & 0xff
        if 0xfea0 <= address < 0xff00:
            return self.unusable_memory_space[address - 0xfea0] & 0xff
        if 0xff00 <= address < 0xff80:
            if address == IO_Registers.P1:
                return self.input.read_input(self.io_ports[0]) & 0xff
            if address in self.apu.registers:
                return self.apu.read_register(address) & 0xff
            if address == IO_Registers.BGPI:
                return self.cgb_palette.get_bgpi()
            if address == IO_Registers.BGPD:
                return self.cgb_palette.get_bgpd()
            if address == IO_Registers.OBPI:
                return self.cgb_palette.get_obpi()
            if address == IO_Registers.OBPD:
                return self.cgb_palette.get_obpd()
            return self.io_ports[address - 0xff00] & 0xff
        if 0xff80 <= address < 0x10000:
            return self.hram[address - 0xff80] & 0xff
        return 0xff

    def write_byte(self, address : int, value : int, hardware_operation : bool = False):
        value = value & 0xff
        if 0 <= address < 0x8000:
            self.rom.write_rom_byte(address, value)
        elif 0x8000 <= address < 0xa000:
            if self.cgb_mode:
                bank = self.read_byte(IO_Registers.VBK) & 0x1
                self.vram[(address - 0x8000)+(0x2000 * bank)] = value
            else:
                self.vram[address - 0x8000] = value
        elif 0xa000 <= address < 0xc000:
            self.rom.write_external_ram_byte(address, value)
        elif 0xc000 <= address < 0xe000:
            if self.cgb_mode:
                if 0xc000 <= address < 0xd000:
                    self.wram[address - 0xc000] = value
                else:
                    bank = self.read_byte(IO_Registers.SVBK) & 0x7
                    self.wram[(address - 0xd000)+(bank*0x1000)] = value
            else:
                self.wram[address - 0xc000] = value
        elif 0xe000 <= address < 0xfe00:
            self.write_byte(address - 0x2000, value) #Echo RAM
        elif 0xfe00 <= address < 0xfea0:
            self.oam[address - 0xfe00] = value
        elif 0xfea0 <= address < 0xff00:
            self.unusable_memory_space[address - 0xfea0] = value
        elif 0xff00 <= address < 0xff80:
            if not hardware_operation:
                if address == IO_Registers.P1:
                    self.io_ports[address - 0xff00] = value & 0b00110000
                elif address == IO_Registers.DIV: # Reset div register
                    self.io_ports[address - 0xff00] = 0x00
                elif address == IO_Registers.DMA: # Start dma transfer
                    self.dma.request_dma_transfer(value)
                elif address == IO_Registers.HDMA5: # Start hdma transfer
                    self.hdma.request_hdma_transfer(value)
                elif address == IO_Registers.BGPI:
                    self.cgb_palette.set_bgpi(value)
                elif address == IO_Registers.BGPD:
                    self.cgb_palette.set_bgpd(value)
                elif address == IO_Registers.OBPI:
                    self.cgb_palette.set_obpi(value)
                elif address == IO_Registers.OBPD:
                    self.cgb_palette.set_obpd(value)
                elif address == 0xff50:
                    self.bootstrap_enabled = False
                elif address in self.apu.registers:
                    self.apu.write_register(address, value)
                #elif address == IO_Registers.KEY1 and self.rom.is_cgb():
                #    mode = self.io_ports[IO_Registers.KEY1 - 0xff00] & 0b10000000
                #    self.hram[IO_Registers.IE - 0xff80] = value
                #    self.io_ports[IO_Registers.P1 - 0xff00] = 0x30
                #    self.io_ports[IO_Registers.KEY1 - 0xff00] = 0 if mode !=0 else 0b10000000
                else:
                    self.io_ports[address - 0xff00] = value
            else:     
                self.io_ports[address - 0xff00] = value
        elif 0xff80 <= address < 0x10000:
            self.hram[address - 0xff80] = value

    def read_word(self, address: int) -> int:
        return (self.read_byte(address) | (self.read_byte(address + 1) << 8)) & 0xffff

    def write_word(self, address : int, value : int):
        value = (value & 0xffff)
        self.write_byte(address, (value & 0xff))
        self.write_byte((address + 1), (value >> 8) & 0xff)
