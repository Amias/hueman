#!/usr/bin/python
#
# This is a script that generates nice ranges of colours
#
# you can specify ranges of hue (0-65535), saturation (0-255) and brightness (0-255)
# these ranges will then constrain the generation of values for each of those keys
# See the .lights files for in the patterns folder for examples

# if you get stuck here run 'pip3 install phue --user' to install the hue control library we use
from phue import Bridge
from pprint import pformat
import time, logging
import argparse
import lxml.etree as etree


def generate_value(light, value):
    """ Generate the next step for a value
    this generates the next value for a given value

    :param light: the light you are generating for
    :param value: which value you want to generate
    :return(str): the value generated
    """

    last = data[light.name][value]
    step = data[light.name][value + '_step']
    direction = data[light.name][value + '_direction']

    max = colour_ranges[value]['max']
    min = colour_ranges[value]['min']

    print("\tN:{0} VN:{1} V:{2} M:{3} D:{4}".format(light.name, value, last, step, direction))

    if last >= max:
        last -= (last - max)
        #modifier = (0 - step)
        direction = 'down'

    if last <= min:
        last += (min - last)
        #modifier = step
        direction = 'up'

    if direction == 'up':
        modifier = step
    else:
        modifier = (0-step)

    generated_value = last + modifier

    global data  # sorry , this sub modifies global data
    data[light.name][value] = generated_value
    data[light.name][value + '_direction'] = direction

    print("\tN:{0} VN:{1} V:{2} M:{3} D:{4}".format(light.name, value, generated_value, modifier, direction))
    return generated_value

# default colour ranges , these will be overriden by config file
colour_ranges = {
    'hue': {
        'min': 5000,
        'max': 10000,
        'step': 2000,
        'skew': 1.05
     },
    'sat': {
        'min': 200,
        'max': 254,
        'step': 15,
        'skew': 2.53
     },
    'bri': {
        'min': 200,
        'max': 254,
        'step': 2,
        'skew': 3.56
    }
}

argparser = argparse.ArgumentParser(description='Control your hue lights')
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
    required=False
)

args = argparser.parse_args()

configfile = args.configfile
bridge_ip = args.bridge_ip

tree = etree.parse(configfile)
root = tree.getroot()

# the bridge we want to use
if not bridge_ip:
    bridge_ip  = root.find('bridge').text

# seconds to sleep between lights, less than 2 can cause requests to be ignored
sleep = float(root.find('sleep').text)
loopsleep = float(root.find('loopsleep').text)

# how long to transition colour in deciseconds  0-300 (0-30 seconds)
transition = int(root.find('transition').text)

name = root.find('name').text

description = root.find('description').text

for keyname in ['hue', 'sat', 'bri']:
    key = root.find(keyname)
    colour_ranges[keyname]['min'] = int(key.find('min').text)
    colour_ranges[keyname]['max'] = int(key.find('max').text)
    colour_ranges[keyname]['step'] = int(key.find('step').text)
    colour_ranges[keyname]['skew'] = float(key.find('skew').text)


# which lights are we using
names = []
for light in root.find('active_lights'):
    names.append(light.text)

bridge = Bridge(bridge_ip)

# if no names where found fetch a list
if len(names) == 0:
    names = bridge.get_light_objects('name')


# generate starting values
data = {}
offset = 0
for key in names:
    offset += 1   # increment offset so we can stagger values by their offsets

    data[key] = {
        'hue': int(colour_ranges['hue']['min'] + (colour_ranges['hue']['step'] * (colour_ranges['hue']['skew'] * offset))),
        'hue_step': colour_ranges['hue']['step'],
        'hue_direction': 'down',
        'sat': int(colour_ranges['sat']['min'] + (colour_ranges['sat']['step'] * (colour_ranges['sat']['skew'] * offset))),
        'sat_step': colour_ranges['sat']['step'],
        'sat_direction': 'down',
        'bri': int(colour_ranges['bri']['min'] + (colour_ranges['bri']['step'] * (colour_ranges['bri']['skew'] * offset))),
        'bri_step': colour_ranges['bri']['step'],
        'bri_direction': 'down',
    }
    # flip the starting direction of every other key
    if offset % 2 == 0:
        data[key]['hue_direction'] = 'up'
        data[key]['sat_direction'] = 'up'
        data[key]['bri_direction'] = 'up'

bridge.logging = 'debug'
logging.basicConfig(filename='random.log', level=logging.DEBUG)

print("Hue Light Patterns by Amias Channer")

if name:
    print("Pattern: {0}".format(name))

if description:
    print("Description: {0}".format(description))

print("Colour Ranges: \n " + pformat(colour_ranges))

# turn all the lights on first
for light in names:
    bridge.set_light(light, 'on', True)

while 1:
    for light in bridge.get_light_objects():
        if light.name in names:
            hue = generate_value(light, 'hue')
            sat = generate_value(light, 'sat')
            bri = generate_value(light, 'bri')

            print("H:{0} S:{1} B:{2} T:{3} N:{4} ".format(hue, sat, bri, transition, light.name))
            params = {
                'on': True,
                'transitiontime': transition,
                'bri': bri,
                'sat': sat,
                'hue': hue,
            }
            light._set(params)
            time.sleep(sleep)
    time.sleep(loopsleep)
exit(0)
