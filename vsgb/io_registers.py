#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum

class IO_Registers(IntEnum):

    P1 = 0xff00 # Register for reading joy pad info and determining system type. (R/W)
    SB = 0xff01 # Serial transfer data (R/W)
    SC = 0xff02 # SIO control  (R/W)
    DIV = 0xff04 # Divider Register (R/W)
    TIMA = 0xff05 # Timer counter (R/W)
    TMA = 0xff06 # Timer Modulo (R/W)
    TAC = 0xff07 # Timer Control (R/W)
    IF = 0xff0f # Interrupt Flag (R/W)
    NR_10 = 0xff10 # Sound Mode 1 register, Sweep register (R/W)
    NR_11 = 0xff11 # Sound Mode 1 register, Sound length/Wave pattern duty (R/W)
    NR_12 = 0xff12 # Sound Mode 1 register, Envelope (R/W)
    NR_13 = 0xff13 # Sound Mode 1 register, Frequency lo (W)
    NR_14 = 0xff14 # Sound Mode 1 register, Frequency hi (R/W)
    NR_21 = 0xff16 # Sound Mode 2 register, Sound Length; Wave Pattern Duty (R/W)
    NR_22 = 0xff17 # Sound Mode 2 register, envelope (R/W)
    NR_23 = 0xff18 # Sound Mode 2 register, frequency lo data (W)
    NR_24 = 0xff19 # Sound Mode 2 register, frequency hi data (R/W)
    NR_30 = 0xff1a # Sound Mode 3 register, Sound on/off (R/W)
    NR_31 = 0xff1b # Sound Mode 3 register, sound length (R/W)
    NR_32 = 0xff1c # Sound Mode 3 register, Select output level (R/W)
    NR_33 = 0xff1d # Sound Mode 3 register, frequency's lower data (W)
    NR_34 = 0xff1e # Sound Mode 3 register, frequency's higher data (R/W)
    NR_41 = 0xff20 # Sound Mode 4 register, sound length (R/W)
    NR_42 = 0xff21 # Sound Mode 4 register, envelope (R/W)
    NR_43 = 0xff22 # Sound Mode 4 register, polynomial counter (R/W)
    NR_44 = 0xff23 # Sound Mode 4 register, counter/consecutive; inital (R/W)
    NR_50 = 0xff24 # Channel control / ON-OFF / Volume (R/W)
    NR_51 = 0xff25 # Selection of Sound output terminal (R/W)
    NR_52 = 0xff26 # Sound on/off (R/W)
    WAVE_PATTERN_START = 0xff30 # Wave Pattern RAM Start address
    WAVE_PATTERN_END = 0xff3f # Wave Pattern RAM End address
    LCDC = 0xff40 # LCD Control (R/W)
    STAT = 0xff41 # LCDC Status   (R/W) 
    SCY = 0xff42 #  Scroll Y   (R/W)
    SCX = 0xff43 # Scroll X   (R/W)
    LY = 0xff44 # LCDC Y-Coordinate (R)
    LYC = 0xff45 # LY Compare  (R/W)
    DMA = 0xff46 # DMA Transfer and Start Address (W)
    BGP = 0xff47 # BG & Window Palette Data  (R/W)
    OBP0 = 0xff48 # Object Palette 0 Data (R/W) 
    OBP1 = 0xff49 # Object Palette 1 Data (R/W)
    WY = 0xff4a # Window Y Position  (R/W)
    WX = 0xff4b # Window X Position  (R/W)
    IE = 0xffff # Interrupt Enable (R/W)


 