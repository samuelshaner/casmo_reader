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
    
*****************************************************
Input
*****************************************************
casmo_reader must be given input of:
- home directory -> The name of the directory you have created on cheezit (e.g. sshaner)
- input file -> The name of the casmo input file (e.g. bwr.inp)
- password -> the password to cheezit

To use, checkout this github repository or copy and paste casmo_reader.py and Helvetica.ttf into a local directory on your computer. Save a casmo input file in this directory as well. The first 5 modules listed above do not come preinstalled with Python, so if you don't have them on your machine, download and install them (It is highly recommended that you use apt-get, MacPorts, HomeBrew, or another package manager to simplify this process). Once you have installed the necessary modules, you can run the code with the command line input below (make sure to insert you directory on cheezit and the cheezit password):

>>> python casmo_reader.py -d 'sshaner' -i 'bwr.inp' -p 'insert_password'

*****************************************************
Notes
*****************************************************
- Include single quotes for each item in the input.
- Upon running casmo_reader, bwr.out and all png files will be deleted from your current working director.
- Pin numbers in bwr.inp can only be numbered 0-9.

*****************************************************
Output
*****************************************************
Plots
- enr.png -> heat map of pin enrichments
- gad.png -> heat map of gadolinium concentration in each pin
- pin_powers##.###.png -> heat map of pin powers for each casmo summary output (~ 55 plots)

Text
- EOL Burnup in MWD / kg
- Max pin power peaking factor
- Initial K_inf
- Max k_inf
- Total fuel cost
- Homework grade















