#!/usr/bin/env python

import json
import argparse
import os

import pandas as pd
import numpy as np
from pyproj import Proj


def main(args):
    # read data file
    df = pd.read_csv('{}.txt'.format(args.input_basename),
                     names=['u', 'v'])
    
    # read header file
    hdr = (pd.read_csv('{}.hdr'.format(args.input_basename),
                   delim_whitespace=True, index_col=0, header=None)
           .to_dict()[1])
    
    yllcorner = float(hdr['yllcorner'])
    xllcorner = float(hdr['xllcorner'])
    ncols = int(hdr['ncols'])
    nrows = int(hdr['nrows'])
    cellsize = float(hdr['cellsize'])

    # find lat/lon coordinates of grid bounds 
    latlon_proj = Proj("+init={}".format(hdr['projection']))

    y_lower, y_upper = yllcorner, yllcorner + nrows * cellsize
    x_left, x_right = xllcorner, xllcorner + ncols * cellsize

    lon_left, lat_lower = latlon_proj(x_left, y_lower, inverse=True)
    lon_right, lat_upper = latlon_proj(x_right, y_upper, inverse=True)

    # rough approximation
    d_lon = (lon_right - lon_left) / ncols
    d_lat = (lat_upper - lat_lower) / nrows
    
    # convert data into JSON
    v_x_data = json.loads(df.u.to_json(orient='values'))
    v_y_data = json.loads(df.v.to_json(orient='values'))

    # add headers (JSON)
    v_x_var = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 2,
            "dx": d_lon, "dy": d_lat,
            "parameterNumberName": "Eastward current",
            "la1": lat_upper,
            "la2": lat_lower,
            "parameterCategory": 2,
            "lo2": lon_right,
            "nx": 383,
            "ny": 142,
            "refTime": "2017-02-01 23:00:00",
            "lo1": lon_left
            },
        'data': v_x_data}

    v_y_var = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 3,
            "dx": d_lon, "dy": d_lat,
            "parameterNumberName": "Northward current",
            "la1": lat_upper,
            "la2": lat_lower,
            "parameterCategory": 2,
            "lo2": lon_right,
            "nx": 383,
            "ny": 142,
            "refTime": "2017-02-01 23:00:00",
            "lo1": lon_left
            },
        'data': v_y_data}

    velocity_field = [v_x_var, v_y_var]
    
    # write JSON file 
    prj_root_path = os.path.dirname(os.path.realpath(__file__)) 
    out_path = os.path.join(prj_root_path,
                            'demo',
                            'velocity-field.json')
    
    with open(out_path, 'w') as outfile:
        json.dump(velocity_field, outfile)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Convert velocities (text format) into "
                     "a leaflet-velocity compatible (json) format."
                     "Creates a new file 'velocity-field.json' "
                     "in the demo directory")
    )
    parser.add_argument("input_basename",
                        help=("basename of input files (two files must exist "
                              "with .txt and .hdr extensions)"))
    
    args = parser.parse_args()
                        
    main(args)
    