#!/usr/bin/env python

import json
import argparse
import os

import pandas as pd
from pyproj import Proj
from pyresample import image, geometry


def resample(field, nrows, ncols, src_area, dest_area):
    field2d = field.reshape((nrows, ncols))

    src_container = image.ImageContainerQuick(field2d, src_area)
    dest_container = src_container.resample(dest_area)

    resampled = dest_container.image_data

    return resampled.flatten()


def main(args):
    # read data file
    df = pd.read_csv('{}.txt'.format(args.input_basename),
                     names=['u', 'v'])

    # read header file
    hdr = (pd.read_csv('{}.hdr'.format(args.input_basename),
                   delim_whitespace=True, index_col=0, header=None)
           .to_dict()[1])

    # get source grid specifications (projected)
    yllcorner = float(hdr['yllcorner'])
    xllcorner = float(hdr['xllcorner'])
    ncols = int(hdr['ncols'])
    nrows = int(hdr['nrows'])
    cellsize = float(hdr['cellsize'])

    y_lower, y_upper = yllcorner, yllcorner + nrows * cellsize
    x_left, x_right = xllcorner, xllcorner + ncols * cellsize

    src_area = geometry.AreaDefinition(
        "src_roi", "projected region of interest",
        "src_proj", {'init': hdr['projection'], 'units': 'm'},
        ncols, nrows,
        (x_left, y_lower, x_right, y_upper)
    )

    # get/find destination grid specifications (lon/lat)
    latlon_proj = Proj("+init={}".format(hdr['projection']))

    lon_left, lat_lower = latlon_proj(x_left, y_lower, inverse=True)
    lon_right, lat_upper = latlon_proj(x_right, y_upper, inverse=True)

    d_lon = (lon_right - lon_left) / ncols
    d_lat = (lat_upper - lat_lower) / nrows

    dest_area = geometry.AreaDefinition(
        'dest_roi', 'lat lon region of interest',
        'dest_proj', {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84'},
        ncols, nrows,
        (lon_left, lat_lower, lon_right, lat_upper)
    )

    # resample u, v velocity components : source grid -> destination grid
    df['u_resampled'] = resample(df.u.values, nrows, ncols, src_area, dest_area)
    df['v_resampled'] = resample(df.v.values, nrows, ncols, src_area, dest_area)

    # prepare leaflet-velocity compatible (data + headers)
    u_data = json.loads(df.u_resampled.to_json(orient='values'))
    v_data = json.loads(df.v_resampled.to_json(orient='values'))

    u_var = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 2,
            "dx": d_lon, "dy": d_lat,
            "parameterNumberName": "Eastward current",
            "la1": lat_upper,
            "la2": lat_lower,
            "parameterCategory": 2,
            "lo2": lon_right,
            "nx": ncols,
            "ny": nrows,
            "refTime": "2017-02-01 23:00:00",
            "lo1": lon_left
            },
        'data': u_data}

    v_var = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 3,
            "dx": d_lon, "dy": d_lat,
            "parameterNumberName": "Northward current",
            "la1": lat_upper,
            "la2": lat_lower,
            "parameterCategory": 2,
            "lo2": lon_right,
            "nx": ncols,
            "ny": nrows,
            "refTime": "2017-02-01 23:00:00",
            "lo1": lon_left
            },
        'data': v_data}

    velocity_field = [u_var, v_var]

    # write JSON file in demo folder
    prj_root_path = os.path.dirname(os.path.realpath(__file__))
    out_path = os.path.join(prj_root_path,
                            'demo',
                            'velocity-field.json')

    with open(out_path, 'w') as outfile:
        json.dump(velocity_field, outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Convert velocities (text format) into "
                     "a leaflet-velocity compatible (json) format, "
                     "after resampled the original data grid onto "
                     "the one used by leaflet. "
                     "Creates a new file 'velocity-field.json' "
                     "in the demo directory")
    )
    parser.add_argument("input_basename",
                        help=("basename of input files (two files must exist "
                              "with .txt and .hdr extensions)"))

    args = parser.parse_args()

    main(args)
