from data_structures import *
from pathlib import Path
import datetime
import hashlib
import argparse
import pickle
import os

class Auditor():
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("path", help="Directory to audit", type=str)
        parser.add_argument("-i", "--input-file", help="Previous audit log file", type=str)
        parser.add_argument("-o", "--output-file", help="New audit log file", type=str)
        parser.add_argument()