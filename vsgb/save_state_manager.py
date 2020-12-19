#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pickle

class SaveStateManager:

    def __init__(self):
        self.version = '1'

    def create(self, emulator):
        temp_rom = emulator.mmu.rom.data
        with open(emulator.cartridge.rom().get_game_id()+'.bin','wb') as save_state_file:
            self.mmu = emulator.mmu
            self.mmu.rom.data = None
            self.ppu = emulator.ppu
            self.hdma = emulator.hdma
            self.dma = emulator.dma
            self.cpu = emulator.cpu
            pickle.dump(self, save_state_file)
        emulator.mmu.rom.data = temp_rom
        logging.info('Saved state')

    def restore(self, emulator):
        try:
            with open(emulator.cartridge.rom().get_game_id()+'.bin','rb') as save_state_file:
                state = pickle.load(save_state_file)
                emulator.mmu = state.mmu
                emulator.mmu.rom.data = emulator.cartridge.rom().data
                emulator.mmu.input = emulator.input
                emulator.ppu = state.ppu
                emulator.hdma = state.hdma
                emulator.dma = state.dma
                emulator.cpu = state.cpu
            logging.info('Loaded state')
        except:
            pass
    