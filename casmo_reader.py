
import numpy
import Image
import ImageDraw

logfile = open("bwr.out", "r").readlines()
summary = 'C A S M O - 4     S U M M A R Y'
powers = numpy.zeros(shape=(10,10))
counter = 0
line_num = 0
for line in logfile:
    if summary in line:
        print logfile[counter+1]
        print 'burnup = ' + logfile[counter+1].split()[2] + ' MWD / kg'
        print 'keff = ' + logfile[counter+1].split()[6]
        print 'peak power = ' + logfile[counter+4].split()[6]
        for i in range(counter+5,counter+15):
            print logfile[i]
            word_start = 2
            for j in range(0,line_num+1):
                powers[line_num,j] = float(logfile[i][word_start]+logfile[i][word_start+1]+logfile[i][word_start+2]+logfile[i][word_start+3]+logfile[i][word_start+4])
                word_start += 7
            line_num += 1

        break
    counter += 1



for row in range(0,10):
    for col in range(row,10):
        powers[row,col] = powers[col,row]

pmax = numpy.max(powers)
powers_draw = powers/pmax

img = Image.new('RGB', (1000,1000), 'white')
draw = ImageDraw.Draw(img)
red = 0
green = 0
blue = 0
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
    
        red = int(255*red)
        green = int(255*green)
        blue = int(255*blue)
    
        draw.rectangle([i*100, j*100, (i+1)*100, (j+1)*100], (red,green,blue))
        draw.text([i*100+40,j*100+50], str(powers[i,j]), (0,0,0))



img.save('pins.png')

print powers
