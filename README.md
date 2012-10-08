casmo_reader
============

camso_reader is a Python script to runs Casmo and plots the results in nice, user-friendly format.


*****************************************************
Dependencies
*****************************************************
Python Modules:
    -   Image (part of Python Imaging Library)
    -   ImageDraw (part of Python Imaging Library)
    -   ImageFont (part of Python Imaging Library)
    -   paramiko (ssh/sftp module)
    -   os
    -   sys
    -   getopt
    -   numpy
    -   math
    
*****************************************************
Input
*****************************************************
casmo_reader must be given input of:
- home directory -> The name of the directory you have created on cheezit (e.g. sshaner)
- input file -> The name of the casmo input file (e.g. bwr.inp)
- password -> the password to cheezit

The input will look like:

>>> python casmo_plotter.py -d 'sshaner' -i 'bwr.inp' -p 'insert_password'

*****************************************************
Notes
*****************************************************
- Include single quotes for each item in the input.
- Upon running casmo_reader, bwr.out and all png files will be deleted from your current working director.

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















