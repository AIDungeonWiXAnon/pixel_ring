import pyaudio
import Queue
import threading


class DoaMic(object):

    def __init__(self, rate=x, channels=8, chunck_size=None):
