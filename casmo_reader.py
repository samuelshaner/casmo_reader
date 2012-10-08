
import Image
import ImageDraw
import paramiko
import os
import sys
import getopt
import numpy

if __name__ == "__main__":
    
    print 'parsing command line input...'
    # parse commandl line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:d:", ["home_dir", "password"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    pass_word = ''
    home_dir = ''
    for o, a in opts:
        if o in ("-p", "--password"):
            pass_word = a
        elif o in ("-d", "--home_dir"):
            home_dir = a
        else:
            assert False, "unhandled option"

    print 'password = ' + pass_word
    print 'home directory = ' + home_dir


    print 'removing old files...'
    # if old files exist, remove them
    if (os.path.exists('bwr.out')):
        os.system('rm bwr.out')
    if (os.path.exists('pin_powers00.000.png')):
        os.system('rm *.png')

    print 'getting casmo output from cheezit...'
    # open transport link to cheezit.mit.edu
    port = 22
    local_path = os.getcwd() + '/bwr.out'
    host = 'cheezit.mit.edu'
    transport = paramiko.Transport((host,port))
    user_name = '22.39'

    # copy bwr.out to local directory
    transport.connect(username=user_name, password = pass_word)
    sftp = paramiko.SFTPClient.from_transport(transport)
    file_path = '/home/22.39/' + home_dir + '/bwr.out'
    sftp.get(file_path, local_path)

    # ssh onto cheezit.mit.edu
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user_name, password = pass_word)

    # get name the last .o file generated
    cmd_str = 'ls ' + home_dir + " -t | grep 'casmo.qsub.o*' | head -n1"
    stdin, stdout, stderr = ssh.exec_command(cmd_str)
    o_file = stdout.readlines()[0]
    o_file = o_file[:-1]

    # copy last .o file to local directory
    file_path = '/home/22.39/' + home_dir + '/' + o_file
    local_path = os.getcwd() + '/' + o_file
    sftp.get(file_path, local_path)

    # close ssh, sftp, and transport
    ssh.close()
    sftp.close()
    transport.close()


    print 'parsing casmo output...'
    # parse output file and make array of pin powers
    logfile = open("bwr.out", "r").readlines()
    summary = 'C A S M O - 4     S U M M A R Y'
    powers = numpy.zeros(shape=(10,10))
    counter = 0
    for line in logfile:
        if summary in line:
            print 'burnup = ' + logfile[counter+1].split()[2] + ' MWD / kg'
            print 'keff = ' + logfile[counter+1].split()[6]
            print 'peak power = ' + logfile[counter+4].split()[6]
            line_num = 0
            for i in range(counter+5,counter+15):
                char_start = 2
                for j in range(0,line_num+1):
                    powers[line_num,j] = float(logfile[i][char_start]+logfile[i][char_start+1]+logfile[i][char_start+2]+logfile[i][char_start+3]+logfile[i][char_start+4])
                    char_start += 7
                line_num += 1


            print 'plotting pin powers...'
            # fill in empty pin powers
            for row in range(0,10):
                for col in range(row,10):
                    powers[row,col] = powers[col,row]

            # create array of normalized pin powers to plot
            pmax = numpy.max(powers)
            powers_draw = powers/pmax

            # create image
            img = Image.new('RGB', (1000,1000), 'white')
            draw = ImageDraw.Draw(img)


            for i in range(0,10):
                for j in range(0,10):
        
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
                    draw.rectangle([i*100, j*100, (i+1)*100, (j+1)*100], (red,green,blue))
                    draw.text([i*100+40,j*100+50], str(powers[i,j]), (0,0,0))


            # save image
            if float(logfile[counter+1].split()[2]) / 10 < 1.0:
                img_str = 'pin_powers0' + logfile[counter+1].split()[2] + '.png'
            else:
                img_str = 'pin_powers' + logfile[counter+1].split()[2] + '.png'
            img.save(img_str)

        counter += 1


