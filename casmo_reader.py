
import Image
import ImageDraw
import ImageFont
import paramiko
import os
import sys
import getopt
import numpy
import math
import time
import matplotlib.pyplot as plt

class Bundle(object):


    def __init__(self, pass_word, user_name, input_file, cluster_name, qsub_file):

        self.pass_word = pass_word
        self.user_name = user_name
        self.input_file = input_file
        self.output_file = input_file[:-3] + 'out'
        self.cluster_name = cluster_name
        self.qsub_file = qsub_file
        self.font = ImageFont.truetype(os.getcwd() + '/Helvetica.ttf', 20)
    
        print 'removing old files...'
        # if old files exist, remove them
        if os.path.exists('plots'):
            os.system('rm -R plots')

        os.system('mkdir plots')
            
        if os.path.exists('input_files') == False:
            os.system('mkdir input_files')

        if os.path.exists('o_files') == False:
            os.system('mkdir o_files')

    
    def makeGeometry(self):
        # parse input file and plot enrichments and gad percents
        print 'parsing casmo input...'
        logfile = open(self.input_file, 'r').readlines()

        for line in logfile:
            if 'PWR' in line:
                self.reactor_type = 'PWR'
                self.num_pins = 17
                self.num_input_pins = 9
            elif 'BWR' in line:
                self.reactor_type = 'BWR'
                self.num_pins = 10
                self.num_input_pins = 10

        self.pin_type = numpy.zeros(shape=(self.num_pins,self.num_pins))
        self.pin_num  = numpy.zeros(shape=(self.num_pins,self.num_pins))

        counter = 0

        for line in logfile:
            if 'LFU' in line:
                line_num = 0
                for i in range(counter+1,counter+self.num_input_pins+1):
                    char_num = 0
                    for j in range(0,line_num+1):
                        if logfile[i][char_num+1] == ' ':
                            self.pin_type[line_num,j] = float(logfile[i][char_num])
                            char_num += 2
                        else:
                            self.pin_type[line_num,j] = float(logfile[i][char_num] + logfile[i][char_num+1])
                            char_num += 3
                    line_num += 1

            counter += 1
        
        counter = 0
        for line in logfile:
    
            if 'LPI' in line:
                line_num = 0
                for i in range(counter+1,counter+self.num_input_pins+1):
                    char_num = 0
                    for j in range(0,line_num+1):
                       self.pin_num[line_num,j] = float(logfile[i][char_num])
                       char_num += 2
                    line_num += 1
            
            counter += 1
        
        # fill in empty pin_types nad pin_nums
        if self.reactor_type == 'BWR':
            for row in range(0,self.num_input_pins):
                for col in range(row,self.num_input_pins):
                    self.pin_type[row,col] = self.pin_type[col,row]
                    self.pin_num [row,col] = self.pin_num [col,row]
        elif self.reactor_type == 'PWR':
            for row in range(0,self.num_input_pins):
                for col in range(row,self.num_input_pins):
                    self.pin_type[row,col] = self.pin_type[col,row]
                    self.pin_num [row,col] = self.pin_num [col,row]
                    
            # fill in empty pins
            for row in range(0,self.num_input_pins)[::-1]:
                for col in range(0,self.num_input_pins)[::-1]:
                    # move to lower right quadrant
                    self.pin_type[col+8,row+8] = self.pin_type[col,row]
                    self.pin_num [col+8,row+8] = self.pin_num [col,row]

            for row in range(0,self.num_input_pins):
                for col in range(0,self.num_input_pins):

                    # reflect about y axis
                    self.pin_type[16-(col+8),row+8] = self.pin_type[col+8,row+8]
                    self.pin_num [16-(col+8),row+8] = self.pin_num [col+8,row+8]

                    # reflect about x axis
                    self.pin_type[col+8,16-(row+8)] = self.pin_type[col+8,row+8]
                    self.pin_num [col+8,16-(row+8)] = self.pin_num [col+8,row+8]

                    # reflect about y axis then x axis
                    self.pin_type[16-(col+8),16-(row+8)] = self.pin_type[col+8,row+8]
                    self.pin_num [16-(col+8),16-(row+8)] = self.pin_num [col+8,row+8]


        
        '''
            This portion of the code parses the  input file for casmo to find the number of each pin type,
            the enrichment for each pin type. It uses this information to compute the total cost for the BWR fuel
            bundle represented by the casmo input file using current fuel costs from the UxC website.
            '''
        
        # parse bwr.inp and find the ids Gd and non-Gd pins
        logfile = open(self.input_file, "r").readlines()
        start_pins = 'FUE'
        end_pins = 'LFU'
        Gd_pin = '64016='
        
        # Dictionaries of pin IDs (keys) to uranium enrichments (values)
        self.non_Gd_pin_IDs_to_enr = {}
        self.Gd_pin_IDs_to_enr = {}

        # Dictionaries of pin IDs (keys) to pin quantities (values)
        self.non_Gd_pin_IDs_to_qty = {}
        self.Gd_pin_IDs_to_qty = {}
        self.pin_IDs_to_gad = {}
        self.non_fuel_pin_IDs_to_qty = {}
        
        line_counter = 0
        
        for line in logfile:
            if start_pins in line:
                
                while start_pins in line:
                    if Gd_pin in line:
                        # First set the number of this given pin to zero - count pins on next loop in script
                        self.Gd_pin_IDs_to_qty[(int(logfile[line_counter].split()[1]))] = 0
                        # Next set the enrichment for this pin type
                        if logfile[line_counter].split()[2][5] == '/':
                            self.Gd_pin_IDs_to_enr[(int(logfile[line_counter].split()[1]))] =  float(logfile[line_counter].split()[2][6:len(logfile[line_counter].split()[2])])
                        else:
                            self.Gd_pin_IDs_to_enr[(int(logfile[line_counter].split()[1]))] =  float(logfile[line_counter].split()[2][5:len(logfile[line_counter].split()[2])])
                        # Next set the gad concentration for this pin type
                        self.pin_IDs_to_gad[(int(logfile[line_counter].split()[1]))] = float(logfile[line_counter].split()[3][6:8])
                    else:
                        # First set number of this given pin to zero - count pins on next loop in script
                        self.non_Gd_pin_IDs_to_qty[(int(logfile[line_counter].split()[1]))] = 0
                        # Next set the enrichment for this pin type
                        if logfile[line_counter].split()[2][5] == '/':
                            self.non_Gd_pin_IDs_to_enr[(int(logfile[line_counter].split()[1]))] = float(logfile[line_counter].split()[2][6:len(logfile[line_counter].split()[2])])
                        else:
                            self.non_Gd_pin_IDs_to_enr[(int(logfile[line_counter].split()[1]))] = float(logfile[line_counter].split()[2][5:len(logfile[line_counter].split()[2])])
                        # Next set the gad concentration for this pin type
                        self.pin_IDs_to_gad[(int(logfile[line_counter].split()[1]))] = 0.0
                    
                    line_counter += 1
                    line = logfile[line_counter]
                
                break
            
            line_counter += 1
        
        # parse input file and find the quantity of each pin type in the geometry
        logfile = open(self.input_file, "r").readlines()
        start_geometry = 'LFU'
        num_non_Gd_pins = 0
        num_Gd_pins = 0
        line_counter = 0
        
        for line in logfile:
            if start_geometry in line:
                
                line_counter += 1
                line = logfile[line_counter]
                
                while line.split():
                    pin_IDs = logfile[line_counter].split()
                    
                    for id in pin_IDs:
                        if int(id) in self.Gd_pin_IDs_to_qty.iterkeys():
                            self.Gd_pin_IDs_to_qty[int(id)] += 1
                            num_Gd_pins += 1
                        elif int(id) in self.non_Gd_pin_IDs_to_qty.iterkeys():
                            self.non_Gd_pin_IDs_to_qty[int(id)] += 1
                            num_non_Gd_pins += 1
                        elif int(id) in self.non_fuel_pin_IDs_to_qty.iterkeys():
                            self.non_fuel_pin_IDs_to_qty[int(id)] += 1                            
                        else:
                            self.non_fuel_pin_IDs_to_qty[int(id)] = 1
                            self.pin_IDs_to_gad[int(id)] = 0.0

                    
                    line_counter += 1
                    line = logfile[line_counter]
                
                break
            
            line_counter += 1
        
        
        # plot enrichments and gad conc.
        self.pin_enr = numpy.zeros(shape=(self.num_pins,self.num_pins))
        self.pin_gad = numpy.zeros(shape=(self.num_pins,self.num_pins))
        for row in range(0,self.num_pins):
            for col in range(0,self.num_pins):
                self.pin_gad   [row,col] = self.pin_IDs_to_gad[int(self.pin_type[row,col])]
                if not self.pin_gad[row,col] == 0:
                    self.pin_enr[row,col] = self.Gd_pin_IDs_to_enr[int(self.pin_type[row,col])]
                elif self.pin_type[row,col] in self.non_fuel_pin_IDs_to_qty.iterkeys():
                    self.pin_enr[row,col] = 0.0
                else:
                    self.pin_enr[row,col] = self.non_Gd_pin_IDs_to_enr[int(self.pin_type[row,col])]

        
        # create array of normalized pin powers to plot
        gad_max = 10
        enr_max = 4.9
        num_max = self.pin_num.max()
        type_max = self.pin_type.max()
        
        pin_enr_draw = self.pin_enr/enr_max
        pin_gad_draw = self.pin_gad/gad_max
        pin_num_draw = self.pin_num/num_max
        pin_type_draw = self.pin_type/type_max

        # create image
        img_enr = Image.new('RGB', (1000,1000), 'white')
        img_gad = Image.new('RGB', (1000,1000), 'white')
        img_num = Image.new('RGB', (1000,1000), 'white')
        img_type = Image.new('RGB', (1000,1000), 'white')
        draw_enr = ImageDraw.Draw(img_enr)
        draw_gad = ImageDraw.Draw(img_gad)
        draw_num = ImageDraw.Draw(img_num)
        draw_type = ImageDraw.Draw(img_type)
        
        
        for i in range(0,self.num_pins):
            for j in range(0,self.num_pins):
                
                # get color for enr pins
                if (pin_enr_draw[i,j] <= 1.0/3.0):
                    red_enr = 0.0
                    green_enr = 3.0 * pin_gad_draw[i,j]
                    blue_enr = 1.0
                elif (pin_enr_draw[i,j] <= 2.0/3.0):
                    red_enr = 3.0 * pin_enr_draw[i,j] - 1.0
                    green_enr = 1.0
                    blue_enr = -3.0 * pin_enr_draw[i,j] + 2.0
                else:
                    red_enr = 1.0
                    green_enr = -3.0 * pin_enr_draw[i,j] + 3.0
                    blue_enr = 0.0
                
                # get color for gad pins
                if (pin_gad_draw[i,j] <= 1.0/3.0):
                    red_gad = 0.0
                    green_gad = 3.0 * pin_gad_draw[i,j]
                    blue_gad = 1.0
                elif (pin_gad_draw[i,j] <= 2.0/3.0):
                    red_gad = 3.0 * pin_gad_draw[i,j] - 1.0
                    green_gad = 1.0
                    blue_gad = -3.0 * pin_gad_draw[i,j] + 2.0
                else:
                    red_gad = 1.0
                    green_gad = -3.0 * pin_gad_draw[i,j] + 3.0
                    blue_gad = 0.0

                # get color for pin nums
                if (pin_num_draw[i,j] <= 1.0/3.0):
                    red_num = 0.0
                    green_num = 3.0 * pin_num_draw[i,j]
                    blue_num = 1.0
                elif (pin_num_draw[i,j] <= 2.0/3.0):
                    red_num = 3.0 * pin_num_draw[i,j] - 1.0
                    green_num = 1.0
                    blue_num = -3.0 * pin_num_draw[i,j] + 2.0
                else:
                    red_num = 1.0
                    green_num = -3.0 * pin_num_draw[i,j] + 3.0
                    blue_num = 0.0

                # get color for pin types
                if (pin_type_draw[i,j] <= 1.0/3.0):
                    red_type = 0.0
                    green_type = 3.0 * pin_type_draw[i,j]
                    blue_type = 1.0
                elif (pin_type_draw[i,j] <= 2.0/3.0):
                    red_type = 3.0 * pin_type_draw[i,j] - 1.0
                    green_type = 1.0
                    blue_type = -3.0 * pin_type_draw[i,j] + 2.0
                else:
                    red_type = 1.0
                    green_type = -3.0 * pin_type_draw[i,j] + 3.0
                    blue_type = 0.0
                
                # convert color to RGB triplet
                red_enr = int(255*red_enr)
                green_enr = int(255*green_enr)
                blue_enr = int(255*blue_enr)
                
                # convert color to RGB triplet
                red_gad = int(255*red_gad)
                green_gad = int(255*green_gad)
                blue_gad = int(255*blue_gad)

                # convert color to RGB triplet
                red_num = int(255*red_num)
                green_num = int(255*green_num)
                blue_num = int(255*blue_num)

                # convert color to RGB triplet
                red_type = int(255*red_type)
                green_type = int(255*green_type)
                blue_type = int(255*blue_type)
                
                # draw pin and pin power
                draw_enr.rectangle([i*100*10.0/self.num_pins, j*100*10.0/self.num_pins, (i+1)*100*10.0/self.num_pins, (j+1)*100*10.0/self.num_pins], (red_enr,green_enr,blue_enr))
                draw_gad.rectangle([i*100*10.0/self.num_pins, j*100*10.0/self.num_pins, (i+1)*100*10.0/self.num_pins, (j+1)*100*10.0/self.num_pins], (red_gad,green_gad,blue_gad))
                draw_num.rectangle([i*100*10.0/self.num_pins, j*100*10.0/self.num_pins, (i+1)*100*10.0/self.num_pins, (j+1)*100*10.0/self.num_pins], (red_num,green_num,blue_num))
                draw_type.rectangle([i*100*10.0/self.num_pins, j*100*10.0/self.num_pins, (i+1)*100*10.0/self.num_pins, (j+1)*100*10.0/self.num_pins], (red_type,green_type,blue_type))
                draw_enr.text([(i*100+35)*10.0/self.num_pins,(j*100+40)*10.0/self.num_pins], str(self.pin_enr[i,j]), (0,0,0), font=self.font)
                draw_gad.text([(i*100+35)*10.0/self.num_pins,(j*100+40)*10.0/self.num_pins], str(self.pin_gad[i,j]), (0,0,0), font=self.font)
                draw_num.text([(i*100+35)*10.0/self.num_pins,(j*100+40)*10.0/self.num_pins], str(int(self.pin_num[i,j])), (0,0,0), font=self.font)
                draw_type.text([(i*100+35)*10.0/self.num_pins,(j*100+40)*10.0/self.num_pins], str(int(self.pin_type[i,j])), (0,0,0), font=self.font)
        
        
        # save images
        img_enr.save('plots/enr.png')
        img_gad.save('plots/gad.png')
        img_num.save('plots/num.png')
        img_type.save('plots/type.png')


    def runCasmo(self):
            
        # open transport link to kilkenny.mit.edu
        port = 22
        local_path = os.getcwd() + '/' + self.output_file
        t = time.gmtime()
        ts = str(t[1]) + '_' + str(t[2]) + '_' + str(t[0]) + '_' + str(t[3]) + ':' + str(t[4]) + ':' + str(t[5])
        base_dir = '/home/' + self.user_name + '/remote_casmo_run_' + ts + '/'

        # connect to cluster
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.cluster_name, username = self.user_name, password = self.pass_word)

        # make remote_casmo_run directory on cluster
        stdin, stdout, stderr = ssh.exec_command('mkdir ' + base_dir)

        # connect to sftp client
        transport = paramiko.Transport((self.cluster_name,port))
        transport.connect(username = self.user_name, password = self.pass_word)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # copy the input file and qsub file to cluster
        print 'transferring input and qsub files to ' + self.cluster_name + '...'
        time.sleep(1)    # allow time to connect to cluster before attempting to transfer files
        sftp.put(self.input_file, base_dir + self.input_file)
        sftp.put(self.qsub_file, base_dir + self.qsub_file)
        
        # submit job on cluster on cluster
        stdin, stdout, stderr = ssh.exec_command('cd ' + base_dir + ' ; qsub ' + self.qsub_file)
        
        # Get the first 3 characters of the name of the job - this is the job id
        job_name = stdout.readlines()[0]
        for i,e in enumerate(job_name):
            if e == '.':
                self.job_id = job_name[0:i]
                break
            
        print 'running casmo job with id: ' + str(self.job_id)

        # Pause and wait for trial to finish
        print 'waiting for ' + self.cluster_name + ' to run casmo....'
        cmd_str = 'qstat | grep ' + str(self.job_id)
        is_file_running = 'initially'
        while (is_file_running is not ''):
            stdin, stdout, stderr = ssh.exec_command(cmd_str)
            try:
                is_file_running = stdout.readlines()[0]
            except:
                break
        
        print 'casmo run complete!'

        # get name of the last .o file generated
        cmd_str = "ls -t " + base_dir + self.qsub_file + ".o* | grep '" + self.qsub_file + ".o*' | head -n1"
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
        self.o_file = stdout.readlines()[0]
        self.o_file = str(self.o_file[:-1])
        self.o_file = self.o_file[len(base_dir):]
                
        # copy casmo .out and .o file to local directory
        print 'getting casmo output from ' + self.cluster_name + '...'
        sftp.get(base_dir + self.output_file, self.output_file[:-4] + '_' + self.job_id + '.out')
        self.output_file = self.output_file[:-4] + '_' + self.job_id + '.out'
        sftp.get(base_dir + self.o_file, 'o_files/' + self.o_file)
        self.o_file = 'o_files/' + self.o_file

        # delete remote_casmo_run directory
        stdin, stdout, stderr = ssh.exec_command('rm -R ' + base_dir)
        
        # close ssh, sftp, and transport
        ssh.close()
        sftp.close()
        transport.close()

    def plotPowers(self):


        print 'parsing casmo output...'
        # parse output file and make array of pin powers
        logfile = open(self.output_file, "r").readlines()
        summary = 'C A S M O - 4     S U M M A R Y'
        self.powers = numpy.zeros(shape=(self.num_pins,self.num_pins))
        counter = 0

        for line in logfile:
            if summary in line:
                burnup_str = 'burnup = ' + logfile[counter+1].split()[2] + ' MWD / kg'
                keff_str = 'keff = ' + logfile[counter+1].split()[6]
                peak_power_str = 'peak power = ' + logfile[counter+4].split()[6]
                line_num = 0
                for i in range(counter+5,counter+5+self.num_input_pins):
                    char_start = 2
                    for j in range(0,line_num+1):
                        self.powers[line_num,j] = float(logfile[i][char_start]+logfile[i][char_start+1]+logfile[i][char_start+2]+logfile[i][char_start+3]+logfile[i][char_start+4])
                        char_start += 7
                    line_num += 1


                if self.reactor_type == 'BWR':
                    for row in range(0,self.num_input_pins):
                        for col in range(row,self.num_input_pins):
                            self.powers[row,col] = self.powers[col,row]
                elif self.reactor_type == 'PWR':
                    for row in range(0,self.num_input_pins):
                        for col in range(row,self.num_input_pins):
                            self.powers[row,col] = self.powers[col,row]
                    
                    # fill in empty pins
                    for row in range(0,self.num_input_pins)[::-1]:
                        for col in range(0,self.num_input_pins)[::-1]:
                            # move to lower right quadrant
                            self.powers[col+8,row+8] = self.powers[col,row]

                    for row in range(0,self.num_input_pins):
                        for col in range(0,self.num_input_pins):

                            # reflect about y axis
                            self.powers[16-(col+8),row+8] = self.powers[col+8,row+8]
                            
                            # reflect about x axis
                            self.powers[col+8,16-(row+8)] = self.powers[col+8,row+8]

                            # reflect about y axis then x axis
                            self.powers[16-(col+8),16-(row+8)] = self.powers[col+8,row+8]

                # create array of normalized pin powers to plot
                pmax = numpy.max(self.powers)
                powers_draw = self.powers/pmax
                
                # create image
                img = Image.new('RGB', (1000,1000), 'white')
                draw = ImageDraw.Draw(img)
                
                
                for i in range(0,self.num_pins):
                    for j in range(0,self.num_pins):
                        
                        # get color
                        if (powers_draw[i,j] <= 1.0/3.0):
                            red = 0.0
                            green = 3.0 * powers_draw[i,j]
                            blue = 1.0
                        elif (powers_draw[i,j] <= 2.0/3.0):
                            red = 3.0 * powers_draw[i,j] - 1.0
                            green = 1.0
                            blue = -3.0 * powers_draw[i,j] + 2.0
                        else:
                            red = 1.0
                            green = -3.0 * powers_draw[i,j] + 3.0
                            blue = 0.0
                        
                        # convert color to RGB triplet
                        red = int(255*red)
                        green = int(255*green)
                        blue = int(255*blue)
                        
                        # draw pin and pin power
                        draw.rectangle([i*100*10.0/self.num_pins, j*100*10.0/self.num_pins, (i+1)*100*10.0/self.num_pins, (j+1)*100*10.0/self.num_pins], (red,green,blue))
                        draw.text([(i*100+15)*10.0/self.num_pins,(j*100+40)*10.0/self.num_pins], str(self.powers[i,j]), (0,0,0), font=self.font)
                
                
                # save image
                sum_str = burnup_str + '  ' + keff_str + '  ' + peak_power_str
                draw.text([250,5], sum_str, font=self.font)
                if float(logfile[counter+1].split()[2]) / 10 < 1.0:
                    img_str = 'plots/pin_powers0' + logfile[counter+1].split()[2] + '.png'
                else:
                    img_str = 'plots/pin_powers' + logfile[counter+1].split()[2] + '.png'
                img.save(img_str)
            
            counter += 1


    def getBaseDepletionParams(self):

        '''
            This portion of the code parses the 'casmo.qsub.o*' condensed output file to find
            the maximum pin power peaking factors, k_inf, and the burnup for each depletion cycle.'
            It finds the maximum power peaking factor for all cycles, the initial k_inf, and the
            maximum burnup (where k_inf < 0.95 indicates EOL).
            '''
        
        logfile = open(self.o_file, "r").readlines()
        start_table = 'TWO-GROUP'
        self.peak_pin_powers = []
        self.k_inf = []
        self.burnup = []
        line_counter = 0
        data_counter = 0
        
        # parse .o file and find the pin powers
        for line in logfile:
            if start_table in line:
                line_counter += 1
                
                # pull the initial k_inf value in the table
                self.peak_pin_powers.append(float(logfile[line_counter].split()[10]))
                self.k_inf.append(float(logfile[line_counter].split()[8]))
                self.burnup.append(float(logfile[line_counter].split()[6]))
                line_counter += 1
                
                # loop over the rest of the table
                while len(line.split()) == 9:
                    if len(line.split()) > 1:
                        self.peak_pin_powers.append(float(logfile[line_counter].split()[5]))
                        self.k_inf.append(float(logfile[line_counter].split()[2]))
                        self.burnup.append(float(logfile[line_counter].split()[1]))
                    
                    # update the counters for the logfile and arrays of data
                    line_counter += 1
                    
                    # fetch the next line in the logfile
                    line = logfile[line_counter]
            
            line_counter += 1

        # plot k_inf vs burnup
        plt.figure()
        plt.plot(self.burnup, self.k_inf)
        plt.xlabel('burnup (MWd/kg)')
        plt.ylabel('k_inf')
        plt.savefig('plots/k_inf_vs_burnup.png')



    def computeGrade(self):

        # compute max pin power and max k_inf
        max_pin_power = max(self.peak_pin_powers)
        initial_k_inf = self.k_inf[0]
        max_k_inf = max(self.k_inf)
        eol_burnup = 0.0
        for i in range(len(self.k_inf)):
            if self.k_inf[i] < .95:
                eol_burnup = self.burnup[i-1] + (self.burnup[i] - self.burnup[i-1]) * \
                    (self.k_inf[i-1] - .95) / (self.k_inf[i-1] - self.k_inf[i])
                break
                                        
        print '\tEOL Burnup = \t\t\t' + str(eol_burnup) + ' [MWD/kg]'
        print '\tMax Pin Power Peaking Factor = \t' + str(max_pin_power)
        print '\tInitial k_inf = \t\t' + str(initial_k_inf)
        print '\tMax k_inf = \t\t\t' + str(max_k_inf)
        
         # Double the quantities of pins to account for a full bundle
        for id in self.Gd_pin_IDs_to_qty.iterkeys():
            self.Gd_pin_IDs_to_qty[id] *= 2
        for id in self.non_Gd_pin_IDs_to_qty.iterkeys():
            self.non_Gd_pin_IDs_to_qty[id] *= 2

        
        # Create a dictionary with key-value pairs of enrichment (w/o) and cost ($/kgU) - 10/5/2013
        U_cost = {2.0 : 573.44, 2.1 : 613.40, 2.2 : 653.61, 2.3 : 694.03, 2.4 : 734.65,
            2.5 : 775.46, 2.6 : 816.43, 2.7 : 857.57, 2.8 : 898.85, 2.9 : 940.26,
            3.0 : 981.81, 3.1 : 1023.47, 3.2 : 1065.25, 3.3 : 1107.13, 3.4 : 1149.11,
            3.5 : 1191.18, 3.6 : 1233.34, 3.7 : 1275.59, 3.8 : 1317.91, 3.9 : 1360.32,
            4.0 : 1402.79, 4.1 : 1445.33, 4.2 : 1487.94, 4.3 : 1530.61, 4.4 : 1573.34,
            4.5 : 1616.12, 4.6 : 1658.96, 4.7 : 1701.86, 4.8 : 1744.80, 4.9 : 1787.79}

        pin_radius = 0.44                   # cm
        pin_length = 409                    # cm
        pin_area = math.pi * pin_radius**2  # cm^2
        pin_volume = pin_area * pin_length  # cm^3
        
        rho_non_Gd_pins = 10.5              # g/cm^3
        rho_Gd_pins = 10.2                  # g/cm^3
        
        tot_cost = 0.0
        burnup_cost = 0.0
        
        non_Gd_pin_mass = pin_volume * rho_non_Gd_pins * 0.001  # kg
        Gd_pin_mass = pin_volume * rho_Gd_pins * 0.001          # kg
        tot_fuel_mass = 0
        
        # loop over the non-Gd pins and add up the cost
        for id in self.non_Gd_pin_IDs_to_qty.iterkeys():
            tot_cost += self.non_Gd_pin_IDs_to_qty[id] * non_Gd_pin_mass * U_cost[self.non_Gd_pin_IDs_to_enr[id]]
            tot_fuel_mass += non_Gd_pin_mass
        
        for id in self.Gd_pin_IDs_to_qty.iterkeys():
            tot_cost += self.Gd_pin_IDs_to_qty[id] * Gd_pin_mass * U_cost[self.Gd_pin_IDs_to_enr[id]]
            tot_fuel_mass += Gd_pin_mass
        
        # convert cost to cents / kW-hr
        burnup_cost = (100*tot_cost) / (eol_burnup*tot_fuel_mass*24*1000)
        
        print '\tTot. Fuel Cost = $' + str(int(tot_cost)) + ' = ' + str(burnup_cost)[0:5] + ' [cents / kWhr]'
                
        # compute the final grade!
        grade = 8*(eol_burnup - 46.5) + 4*(1.30 - max_pin_power) + 2*(1.11 - max_k_inf) - 25*burnup_cost
        print '\tYour final grade is: \t\t' + str(int(grade))

        with open(self.input_file, 'a') as input_file:
            input_file.write('* GRADE: ' + str(grade))


def main():
    
    print 'parsing command line input...'

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:u:i:c:q:", ["username", "password", "inputfile", "clustername", "qsubfile"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    pass_word = ''
    user_name = ''
    input_file = ''
    cluster_name = ''
    qsub_file = ''

    for o, a in opts:
        if o in ("-p", "--password"):
            pass_word = str(a)
        elif o in ("-u", "--username"):
            user_name = str(a)
        elif o in ("-i", "--inputfile"):
            input_file = str(a)
        elif o in ("-c", "--clustername"):
            cluster_name = str(a)
        elif o in ("-q", "--qsubfile"):
            qsub_file = str(a)
        else:
            assert False, "unhandled option"

    bundle = Bundle(pass_word, user_name, input_file, cluster_name, qsub_file)

    bundle.makeGeometry()
    bundle.runCasmo()
    
    # copy .inp file to unique .inp file
    os.system('cp ' + str(input_file) + ' input_files/' + input_file[:-4] + '_' + str(bundle.job_id) + '.inp')
    bundle.input_file = 'input_files/' + input_file[:-4] + '_' + str(bundle.job_id) + '.inp'

    bundle.plotPowers()
    bundle.getBaseDepletionParams()

    if bundle.reactor_type == 'BWR':
        bundle.computeGrade()

    # remove the .out file
    os.system('rm ' + str(bundle.output_file))


if __name__ == '__main__':

    main()










