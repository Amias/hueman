hueman
======

Some simple scripts to control your hue lights from the command line using phue

you need phue installed , to do this 

```shell
pip install phue --user
```
Before you run one of these scripts for the first time you need to press the
buttom on the bridge to allow it to connect, if you don't the script will fail.

to colorloop all your hues 
```shell
./colour_loop -b ip.ad.dr.es 
./colour_loop -b ip.ad.dr.es -m off
```

to flash all your hues
```shell
./alert -b ip.ad.dr.es -m lselect
./alert -b ip.ad.dr.es -m select
./alert -b ip.ad.dr.es -m none
```

to run a lights sequence
```shell
./hue_light_patterns -c patterns/meditate.lights 
```
