#!/usr/bin/python
#
# This is a script that flashes all the hues
#

from phue import Bridge
import logging
import time
import argparse
import lxml.etree as etree

argparser = argparse.ArgumentParser(description='flash your hue lights')
argparser.add_argument(
    '--config', '-c',
    dest='configfile',
    help='.lights file to load',
    required=False
)
argparser.add_argument(
    '--bridge', '-b',
    dest='bridge_ip',
    help='ip of the hue bridge to use',
    default=False
)
argparser.add_argument(
    '--mode', '-m',
    dest='mode',
    choices=['lselect', 'select', 'none'],
    help='flash mode of the hue bridge to use',
    default='select'
)
args = argparser.parse_args()

configfile = args.configfile
bridge_ip = args.bridge_ip
mode = args.mode

names = []
name = False
description = False

# the bridge we want to use
if not bridge_ip:
    tree = etree.parse(configfile)
    root = tree.getroot()
    bridge_ip = root.find('bridge').text

    name = root.find('name').text
    description = root.find('description').text

    # which lights are we using
    for light in root.find('active_lights'):
        names.append(light.text)

bridge = Bridge(bridge_ip)

# if no names where found fetch a list
if len(names) == 0:
    names = bridge.get_light_objects('name')

bridge.logging = ('debug')
logging.basicConfig(filename='random.log', level=logging.DEBUG)

print "Set all Hue Lights to Flash by Amias Channer"

if name:
    print "Pattern: {0}".format(name)

if description:
    print "Description: {0}".format(description)

for light in bridge.get_light_objects():
    if light.name in names:
        params = {
                'on': True,
                'alert': mode,
                'bri': 255,
        }
        light._set(params)
        time.sleep(1)
