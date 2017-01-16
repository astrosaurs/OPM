#!/usr/bin/python
"""
    create_opm.py
    ---------------Description---------------
    Create OPM from STK segment summary
    -----------------Inputs------------------
    None (for now) - customize inputs in script
    -----------------Outputs-----------------
    Three TLE files for each operational satellite:
    OPM format file
    ------------
    """

# Custom Inputs
#filename = "Helio_Test Initial State.txt"
filename = "2009 Perigee.txt"
param_set_type = 'Cartesian'    # use cartesian coordinate system (can only handle this currently)
originator = "B612-jcarrico"
object_name = "AvAstSat"
object_id = "2020-900Z"

# Import Libraries
import datetime as dt
import os
import sys

# Parse Data Function
def parse(data, string, split=False):
    match = [s for s in data if string in s]
    match_string = match[0].strip()
    
    if split:
        param = match_string.split()
    else:
        param = match_string
    
    return param

def main():
    tempfile = "tempfile.txt" # used for stripping all blank lines

    with open(tempfile, 'w') as f:
        with open(filename,'r') as file:
            for line in file:
                if not line.isspace():
                    f.write(line)

    # Open Temp File
    with open(tempfile) as f:
        content = f.readlines()

    # Get Creation Date
    date = content[0].strip()
    date_opm = dt.datetime.strptime(date, '%d %b %Y %H:%M:%S').strftime('%Y-%m-%d')

    # Get Epoch and Time System
    epoch_string = "Time past epoch"
    epoch_match = parse(content, epoch_string)

    t = epoch_match.split("(")[1]
    epoch = t.split(": ")[1][:-1]

    epstr = "Epoch in "
    index = epoch_match.find(epstr)

    if epoch_match[index+9:index+12] == "UTC":
        time_sys = "UTC"
    else:
        time_sys = "N/A"

    # Get Frame Body and Coordinate System
    frame_string = "State Vector in Coordinate System"
    frame_match = parse(content, frame_string)

    frame = frame_match.split(": ")[1]
    frame_array = frame.split(" ")
    body = frame_array[0].upper()
    coord = frame_array[1]

    # Get State Vector
    coord_match = [s for s in content if param_set_type in s]
    ind = content.index(coord_match[0])

    x = content[ind+1].strip().split()    # x position and velocity
    y = content[ind+2].strip().split()    # y position and velocity
    z = content[ind+3].strip().split()    # z position and velocity

    # Get Spacecraft Config Params

    mass_string = "Total Mass"
    mass = parse(content, mass_string, True)

    SRParea_string = "SRP Area"
    SRParea = parse(content, SRParea_string, True)

    SRPcoeff_string = "Cr:"
    SRPcoeff = parse(content, SRPcoeff_string, True)

    dragArea_string = "Drag Area"
    dragArea = parse(content, dragArea_string, True)

    dragCoeff_string = "Cd:"
    dragCoeff = parse(content, dragCoeff_string, True)

    # Remove Temp File
    os.remove("tempfile.txt")

    # Write to File
    with open(filename[:-3] + 'opm', 'w') as f:
        f.write("CCSDS_OPM_VERS = 2.0" + "\n")
        f.write("CREATION_DATE = %s" % date_opm + "\n")
        f.write("ORIGINATOR = %s" % originator + "\n")
        f.write("COMMENT %s coordinate system" % param_set_type + "\n")
        f.write("OBJECT_NAME = %s" % object_name + "\n")
        f.write("OBJECT_ID = %s" % object_id + "\n")
        f.write("CENTER_NAME = %s" % body + "\n")
        f.write("REF_FRAME = %s" % coord + "\n")
        f.write("TIME_SYSTEM = %s" % time_sys + "\n")
        f.write("EPOCH = %s" % epoch + "\n")
        f.write("X =  %s [%s]" %(x[1], x[2]) + "\n")
        f.write("Y =  %s [%s]" %(y[1], y[2]) + "\n")
        f.write("Z =  %s [%s]" %(z[1], z[2]) + "\n")
        f.write("X_DOT =   %s [%s]" %(x[-2], x[-1]) + "\n")
        f.write("Y_DOT =   %s [%s]" %(y[-2], y[-1]) + "\n")
        f.write("Z_DOT =   %s [%s]" %(z[-2], z[-1]) + "\n")
        f.write("MASS = %s [%s]" %(mass[-2], mass[-1]) + "\n")
        f.write("SOLAR_RAD_AREA = %s    [%s]" %(SRParea[-2], SRParea[-1].replace("^", "**")) + "\n")
        f.write("SOLAR_RAD_COEFF = %s" %(SRPcoeff[-1]) + "\n")
        f.write("DRAG_AREA = %s    [%s]" %(dragArea[-2], dragArea[-1].replace("^", "**")) + "\n")
        f.write("DRAG_COEFF = %s" %(dragCoeff[-1]))

if __name__ == "__main__":
    main(*sys.argv[1:])
