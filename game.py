#!/usr/bin/python3

from os import path

ROOT_DIR = path.dirname(path.abspath(__file__))
RESOURCE_DIR = path.join(ROOT_DIR, 'resources')

from src.sdl_main import PyCraft
game = PyCraft(RESOURCE_DIR)
