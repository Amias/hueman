import phue
import logging
import random
import colorsys

def generate_hls(red,green,blue):
    return colorsys.rgb_to_hls(red, green, blue)


logger = logging.getLogger('phue')
console = logging.StreamHandler()

console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console.setFormatter(formatter)
logger.addHandler(console)

rmin = 10
rmax = 255

gmin = 10
gmax = 255

bmin = 10
bmax = 255

try:
    bridge = phue.Bridge('192.168.1.22')
    bridge.logging=('debug')
    bridge.connect()
    bridge.get_api()
    light_names=bridge.get_light_objects('name')

except OSError as e:
    print("Error: connecting to bridge: {0}".format(e))

names = []

for light in lights:
    print("Selected light: {0} \n  {1}".format(light.name, light))
    for key in light.__dict__:
        print("Key: {0} = {1}".format(key, light.__dict__[key]))

    for r in range(rmin, rmax):
        for g in range(gmin, gmax):
            for b in range(bmin, bmax):
                value = generate_hls(r, g, b)
                colour = {'hue': value[0], 'sat': value[2], 'bri': value[1]}
                bridge.set_light(light.name, colour)
    bridge.set_light(light.name, 'on', False)
