from argparse import ArgumentParser
# import sys
import os
#from subprocess import Popen, PIPE
# import re

parser = ArgumentParser("Run network commands")
# parser.add_argument(
#     '--device',
#     help="The device's name (eg. router1, router2, etc.)"
# )
parser.add_argument('--cmd', default='ifconfig',
                    nargs="+",
                    help="Command to run inside node.")

FLAGS = parser.parse_args()

def main():
    cmd = ' '.join(FLAGS.cmd)
    os.system(cmd)


if __name__ == '__main__':
    main()