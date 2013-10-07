casmo_reader
============

camso_reader is a Python script to runs Casmo and plots the results in nice, user-friendly format.


*****************************************************
Dependencies
*****************************************************
Python Modules:
- Image (part of Python Imaging Library)
- ImageDraw (part of Python Imaging Library)
- ImageFont (part of Python Imaging Library)
- paramiko (ssh/sftp module)
- numpy
- os
- sys
- getopt
- math
- time
    
*****************************************************
Input
*****************************************************
casmo_reader must be given input of:
- cluster    [-c]   -> the cluster you want to run the code on (e.g. mycluster.mit.edu)
- username   [-u]   -> Your username for the cluster
- password   [-p]   -> Your password for the cluster
- input file [-i]   -> The name of the casmo input file (e.g. ge14.inp)
- qsub file  [-q]   -> The name of your qsub file (e.g. casmo.qsub)

To use, checkout this github repository. A sample input file (ge14.inp) has been included and users are recommended to modify this input file to avoid errors (casmo_reader is a bit finnicky with input files). The first 5 modules listed above do not come preinstalled with Python, so if you don't have them on your machine, download and install them (It is highly recommended that you use apt-get, MacPorts, HomeBrew, pip, or another package manager to simplify this process). Once you have installed the necessary modules, you can run the code with the command line input below (make sure to input the proper flags for your username, password, cluster, input file, and qsub file):

>>> python casmo_reader.py -c mycluster.mit.edu -u myusername -p mypassword -i ge14.inp -q casmo.qsub

If you have already run your simulation and have the .o file, you can process the output files and compute your grade with the following command

>>> python casmo_reader.py -i ge14.inp -o casmo.qsub.o######

Where you replace ge14.inp with your input file and casmo.qsub.o##### with the .o file for your run.

*****************************************************
Notes
*****************************************************
- Upon running casmo_reader, any .out files with the same base input file name and all png files will be overwritten.
- Pin numbers in the input file can only be numbered 1-9.
- There must be a blank line after the end of the LFU section.
- You are also able to run octant symmetric PWR assemblies, but no grade will be computed.

*****************************************************
Output
*****************************************************
Plots
- enr.png  -> heat map of pin enrichments
- gad.png  -> heat map of gadolinium concentration in each pin
- num.png  -> heat map of LPI pin numbers
- type.png -> heat map of LFU pin types
- pin_powers##.###.png -> heat map of pin powers for each casmo summary output (~ 55 plots)

Text
- EOL Burnup in MWD / kg
- Max pin power peaking factor
- Initial K_inf
- Max k_inf
- Total fuel cost (Uranium price update on 10/5/13)
- Homework grade (For 2012 assignment weights)















