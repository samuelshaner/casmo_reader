import math



#######################################################################################
#################                 Compute Your Grade                ###################
#######################################################################################


'''
This portion of the code parses the 'casmo.qsub.o*' condensed output file to find
the maximum pin power peaking factors, k_inf, and the burnup for each depletion cycle.'
It finds the maximum power peaking factor for all cycles, the initial k_inf, and the
maximum burnup (where k_inf < 0.95 indicates EOL).
'''

logfile = open("casmo.qsub.o954", "r").readlines()
start_table = 'TWO-GROUP'
end_table = 'RUN TERMINATED'
peak_pin_powers = []
k_inf = []
burnup = []
line_counter = 0
data_counter = 0

# parse casmo.qsub.o954 and find the 
for line in logfile:
    if start_table in line:
        line_counter += 1

        # pull the initial k_inf value in the table
        peak_pin_powers.append(float(logfile[line_counter].split()[10]))
        k_inf.append(float(logfile[line_counter].split()[8]))
        burnup.append(float(logfile[line_counter].split()[5]))
        line_counter += 1

        # loop over the rest of the table
        while end_table not in line:

            # Check that this k_inf is not beyond EOL 
            if (k_inf[len(k_inf)-1] > 0.95):

                peak_pin_powers.append(float(logfile[line_counter].split()[5]))
                k_inf.append(float(logfile[line_counter].split()[2]))
                burnup.append(float(logfile[line_counter].split()[1]))

            # update the counters for the logfile and arrays of data
            data_counter += 1
            line_counter += 1

            # fetch the next line in the logfile
            line = logfile[line_counter]

    line_counter += 1


# readjust to only include data for k_inf > 0.95 (EOL)
peak_pin_powers = peak_pin_powers[0:len(peak_pin_powers)-1]
k_inf = k_inf[0:len(k_inf)-1]
burnup = burnup[0:len(burnup)-1]

# compute max pin power and max k_inf
max_pin_power = max(peak_pin_powers)
initial_k_inf = k_inf[0]
max_k_inf = max(k_inf)
eol_burnup = max(burnup)

print '\tEOL Burnup = \t\t\t' + str(eol_burnup) + ' [MWD/kg]'
print '\tMax Pin Power Peaking Factor = \t' + str(max_pin_power)
print '\tInitial k_inf = \t\t' + str(initial_k_inf)
print '\tMax k_inf = \t\t\t' + str(max_k_inf)


'''
This portion of the code parses the 'bwr.inp' input file for casmo to find the number of each pin type,
the enrichment for each pin type. It uses this information to compute the total cost for the BWR fuel
bundle represented by the casmo input file using current fuel costs from the UxC website.
'''

# parse bwr.inp and find the ids Gd and non-Gd pins
inputfile = open("bwr.inp", "r").readlines()
start_pins = 'FUE'
end_pins = 'LFU'
Gd_pin = '64016='

# Dictionaries of pin IDs (keys) to uranium enrichments (values)
non_Gd_pin_IDs_to_enr = {}
Gd_pin_IDs_to_enr = {}

# Dictionaries of pin IDs (keys) to pin quantities (values)
non_Gd_pin_IDs_to_qty = {}
Gd_pin_IDs_to_qty = {}

line_counter = 0

for line in inputfile:
    if start_pins in line:        

        while start_pins in line:
            if Gd_pin in line:
                # First set the number of this given pin to zero - count pins on next loop in script
                Gd_pin_IDs_to_qty[(int(inputfile[line_counter].split()[1]))] = 0
                # Next set the enrichment for this pin type
                Gd_pin_IDs_to_enr[(int(inputfile[line_counter].split()[1]))] =  float(inputfile[line_counter].split()[2][5:len(inputfile[line_counter].split()[2])])
            else:
                # First set number of this given pin to zero - count pins on next loop in script
                non_Gd_pin_IDs_to_qty[(int(inputfile[line_counter].split()[1]))] = 0
                # Next set the enrichment for this pint type
                non_Gd_pin_IDs_to_enr[(int(inputfile[line_counter].split()[1]))] = float(inputfile[line_counter].split()[2][5:len(inputfile[line_counter].split()[2])])
                
            line_counter += 1
            line = inputfile[line_counter]

        break

    line_counter += 1


# parse bwr.inp and find the quantity of each pin type in the geometry
inputfile = open("bwr.inp", "r").readlines()
start_geometry = 'LFU'
end_geometry = 'DEP'
num_non_Gd_pins = 0
num_Gd_pins = 0
line_counter = 0

for line in inputfile:
    if start_geometry in line:

        line_counter += 1
        line = inputfile[line_counter]

        while end_geometry not in line:
            pin_IDs = inputfile[line_counter].split()
            
            for id in pin_IDs:
                if int(id) in Gd_pin_IDs_to_qty.iterkeys():
                    Gd_pin_IDs_to_qty[int(id)] += 1
                    num_Gd_pins += 1
                else:
                    non_Gd_pin_IDs_to_qty[int(id)] += 1
                    num_non_Gd_pins += 1
                
            line_counter += 1
            line = inputfile[line_counter]

        break

    line_counter += 1


# Hack to account for the water pins
non_Gd_pin_IDs_to_qty[2] -= 4

# Double the quantities of pins to account for a full bundle
for id in Gd_pin_IDs_to_qty.iterkeys():
    Gd_pin_IDs_to_qty[id] *= 2
for id in non_Gd_pin_IDs_to_qty.iterkeys():
    non_Gd_pin_IDs_to_qty[id] *= 2


# Create a dictionary with key-value pairs of enrichment (w/o) and cost ($/kgU) - 10/7/2012
U_cost = {2.0 : 727.36, 2.1 : 777.87, 2.2 : 828.67, 2.3 : 879.74, 2.4 : 931.06, 
          2.5 : 982.60, 2.6 : 1034.36, 2.7 : 1086.31, 2.8 : 1138.44, 2.9 : 1190.74, 
          3.0 : 1243.20, 3.1 : 1295.81, 3.2 : 1384.55, 3.3 : 1401.43, 3.4 : 1454.43, 
          3.5 : 1507.54, 3.6 : 1560.77, 3.7 : 1614.09, 3.8 : 1667.52, 3.9 : 1721.04, 
          4.0 : 1774.65, 4.1 : 1828.34, 4.2 : 1882.12, 4.3 : 1935.97, 4.4 : 1989.89, 
          4.5 : 2042.89, 4.6 : 1097.96, 4.7 : 2152.08, 4.8 : 2206.28, 4.9 : 2260.53}

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
for id in non_Gd_pin_IDs_to_qty.iterkeys():
    tot_cost += non_Gd_pin_IDs_to_qty[id] * non_Gd_pin_mass * U_cost[non_Gd_pin_IDs_to_enr[id]]
    tot_fuel_mass += non_Gd_pin_mass

for id in Gd_pin_IDs_to_qty.iterkeys():
    tot_cost += Gd_pin_IDs_to_qty[id] * Gd_pin_mass * U_cost[Gd_pin_IDs_to_enr[id]]
    tot_fuel_mass += Gd_pin_mass

# convert cost to cents / kW-hr
burnup_cost = (100*tot_cost) / (eol_burnup*tot_fuel_mass*24*1000)

print '\tTot. Fuel Cost = $' + str(int(tot_cost)) + ' = ' + str(int(burnup_cost)) + ' [cents / kWhr]'


# compute the final grade!
grade = 8*(eol_burnup - 46.5) + 4*(1.30 - max_pin_power) + 2*(1.11 - max_k_inf) - 25*burnup_cost
print '\tYour final grade is: \t\t' + str(int(grade))
