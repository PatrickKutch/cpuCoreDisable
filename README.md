# cpuCoreDisable - ccd.py 
---------------
This simple utility will disable cpu cores on a physical CPU package.  You may disable all the cores on a physical CPU package, or you can disable all of the hyperthread cores on a physical package.

So for example if you want to do some testing without hyperthreading, then you can run this tool a coouple of times to disable hyperthreads on each CPU (assuming you have two) as such:

python ccd.py hyperthread --package 0
python ccd.py hyperthread --package 1

You may also wish to disable an entire CPU, so you can test stuff.  Rather than physically removing one of the CPU's or changing boot parameters you can do this:

python ccd.py disablepackage --package 1

This will disable all of the cores on physical CPU 1.  Many OS's will not allow you to do this to physical CPU 0.

The individual CPU cores are taken offline by writing a '0' to '/sys/devices/system/cpu/cpu#/online' file.

## NOTE - after you disable a CPU, you must reboot to get it back