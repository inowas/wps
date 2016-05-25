# -*- coding: utf-8 -*-
"""
Created on Thu May 19 14:24:38 2016

@author: aybulat

This is script for running a service for preprocessing input data, execution of a Modflow model and postprocessing results.
Service's module structure: main.py/imports/model.py
                                           /utils/intersector.py
                                                 /ibound.py
                                                 /line_boundary.py

Features so far include: variable resolution, number of layers, layers properties, stress periods
CHD boundary condition with line-point interpolation tool. 

Layer properties given with rasters have to be finished and tested

Things to add: well and river BC type, initial head definition (in this version is taken from top elevation).

Postprocessing include calculation of ['mean', 'raw', 'delta', 'max', 'min', 'standard_deviation'] property arrays 
for the given time steps of interest, result saved in 'responce_raster'

Modflow working directory have to be changed

This file's structure will be changed depending on requirements of the implemented web serving technology

"""
from urllib import urlopen
import json
import numpy as np
import os
import sys
import flopy

from imports import model

# Sample input data #####################################################
sample_data = {"model_id": "671fc907-a0e4-4fff-a960-ca125273e2bc",
               "calculate": True,
               "nx": 50,
               "ny": 50,
               "give_raster": True,
               "time_steps_of_interest": [10,20],
               "layer_of_interest": 1,
               "operation": "mean"}
request_data = sample_data
working_directory = '/home/aybulat/Desktop/git/postgres_flopy/pywps_flopy'
##########################################################################

def create_and_run(workspace, data, nx, ny):
    try:    
        m = model.Model()
        m.setFromJson(data)
        m.set_properties(nx,ny)
        m.run_model(workspace)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    else:
        print 'model created, calculated and saved'
    
    
    
def read_output(workspace, name, timesteps, layer, operation):
    try:    
        possible_operations = ['mean', 'raw', 'delta', 'max', 'min', 'standard_deviation']
        if operation not in possible_operations:
            print 'requested operation is not available'
            return
        head_file_objects = flopy.utils.HeadFile(os.path.join(workspace, name+'.hds'))
        heads_ts = [head_file_objects.get_data(totim = timestep) for timestep in timesteps]
        heads_ts_array = np.array([heads[layer].tolist() for heads in heads_ts])
        if operation == 'mean':
            return np.mean(heads_ts_array, axis = 0)
        elif operation == 'raw':
            return heads_ts_array
        elif operation == 'delta':
            return heads_ts_array[-1] - heads_ts_array[0]
        elif operation == 'max':
            return np.max(heads_ts_array, axis = 0)
        elif operation == 'min':
            return np.min(heads_ts_array, axis = 0)
        elif operation == 'standard_deviation':
            return np.std(heads_ts_array, axis = 0)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    else:
        print 'raster produced'

#######################################################################################################
responce = urlopen('http://app.dev.inowas.com/api/models/' + request_data['model_id'] + '.json').read()
jsonData = json.loads(responce)

# modflow workspace
workspace = working_directory + request_data['model_id']

if not os.path.exists(workspace):
    if request_data['calculate']:
        os.makedirs(workspace)
    else:
        print 'model does not exist, first calculate'
        quit()

if request_data['calculate']: 
    create_and_run(workspace, jsonData, request_data['nx'], request_data['ny'])

if request_data['give_raster']:
    responce_raster = read_output(workspace, request_data['model_id'], 
                                  request_data['time_steps_of_interest'], request_data['layer_of_interest'],
                                  request_data['operation'])
#######################################################################################################