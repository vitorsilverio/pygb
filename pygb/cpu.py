#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from pygb.interrupt_manager import InterruptManager, Interrupt
from pygb.instruction_performer import InstructionPerformer
from pygb.io_registers import IO_Registers
from pygb.mmu import MMU
from pygb.registers import Registers
from pygb.stack_manager import StackManager
from pygb.timer import Timer

class CPU:

    def __init__(self,mmu: MMU):
        self.mmu = mmu
        self.registers = Registers()
        self.interruptManager = InterruptManager(mmu)
        self.timer = Timer(mmu, self.interruptManager)
        self.stackManager = StackManager(self.registers, self.mmu)
        self.instructionPerformer = InstructionPerformer(self)
        self.ticks = 0
        self.ime = False
        self.halted = False
        self.stop = False
        self.pc_before_interrupt = 0x0000
        self.pending_interrupts_before_halt = 0x00
        
    def step(self) -> None:
        self.ticks = 0
        if self.stop:
            return None
        self.check_halted()
        if self.ime or self.pending_interrupts_before_halt != 0:
            self.serve_interrupt()
        if self.halted:
            self.ticks += 4
        else:
            instruction = self.fetch_instruction()
            self.perform_instruction(instruction)
        self.timer.tick(self.ticks)
    
    def check_halted(self) -> None:
        if self.halted and self.pending_interrupts_before_halt != self.mmu.read_byte(IO_Registers.IF):
            self.ticks += 4
            self.halted = False

    def serve_interrupt(self) -> None:
        interrupt = self.interruptManager.pending_interrupt()
        if interrupt == Interrupt.INTERRUPT_NONE:
            return None
        self.ime = False
        if self.halted:
            self.halted = False
        self.stackManager.push_word(self.registers.pc)
        self.pc_before_interrupt = self.registers.pc
        if_register = self.mmu.read_byte(IO_Registers.IF)
        if interrupt == Interrupt.INTERRUPT_VBLANK:
            self.registers.pc = 0x40 #RST 40H
            self.mmu.write_byte(IO_Registers.IF, if_register & 0b11111110)
        if interrupt == Interrupt.INTERRUPT_LCDSTAT:
            self.registers.pc = 0x48 #RST 48H
            self.mmu.write_byte(IO_Registers.IF, if_register & 0b11111101)
        if interrupt == Interrupt.INTERRUPT_TIMER:
            self.registers.pc = 0x50 #RST 50H
            self.mmu.write_byte(IO_Registers.IF, if_register & 0b11111011)
        if interrupt == Interrupt.INTERRUPT_SERIAL:
            self.registers.pc = 0x58 #RST 58H
            self.mmu.write_byte(IO_Registers.IF, if_register & 0b11110111)
        if interrupt == Interrupt.INTERRUPT_JOYPAD:
            self.registers.pc = 0x60 #RST 60H
            self.mmu.write_byte(IO_Registers.IF, if_register & 0b11101111)
        self.ticks += 20

    def fetch_instruction(self, prefix: bool = False) -> int:
        instruction = self.mmu.read_byte(self.registers.pc)
        self.registers.pc += 1
        if instruction == 0xcb and not prefix:
            return 0xcb00 + self.fetch_instruction(True)
        return instruction

    def perform_instruction(self, instruction : int) -> None:
        self.ticks += self.instructionPerformer.perform_instruction(instruction)



