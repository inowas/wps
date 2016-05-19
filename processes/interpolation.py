# -*- coding: utf-8 -*-
"""
Created on Wed May 18 12:46:12 2016

@author: aybulat
"""

from pywps.Process import WPSProcess
from pyKriging.krige import kriging 
import numpy as np
import demjson

class InterpolationProcess(WPSProcess):
    """
    WPS implementation of pyKriging using default parameters.
    Data input format: '{"type":"kriging", "bounding_box":{"x_min":0, "x_max": 10, "y_min": 0, "y_max": 10}, "grid_size":{"n_x":20, "n_y":12},"point_values":[{"x":1,"y":4,"value":0.01},{"x":3.2,"y":2,"value":0.44},{"x":5,"y":5,"value":0.1},{"x":6,"y":8,"value":0.99}]}'
    """

    def __init__(self):
        WPSProcess.__init__(self, identifier = "interpolation", title="Interpolation process")

        self.array_string_out = self.addComplexOutput(identifier="arrayJSON", title="Array string", formats=[{"mimeType":"text/json"}])
        self.json_string_in = self.addComplexInput(identifier="interpolationData", title="Interpolation data", formats=[{"mimeType":"text/json"}])
    
    def execute(self): 
        with open(str(self.json_string_in.getValue()), 'r') as files:
            string = files.read()

        print string
        json_dict = demjson.decode(string)
        method = json_dict['type']
        xmin, xmax, ymin, ymax = float(json_dict['bounding_box']['x_min']), float(json_dict['bounding_box']['x_max']), float(json_dict['bounding_box']['y_min']), float(json_dict['bounding_box']['y_max'])
        nx, ny = json_dict['grid_size']['n_x'], json_dict['grid_size']['n_y']
        dx = (xmax - xmin) / nx
        dy = (ymax - ymin) / ny
        X = []
        y = []
        for point in json_dict['point_values']:
            X.append([point['y'], point['x']])
            y.append(point['value'])
        
        self.grid = np.zeros((ny,nx))
        
        if method == 'kriging':
            k = kriging(np.array(X), np.array(y))
            self.status.set('training model...')
            k.train()
            self.status.set('predicting grid values...')
            for i in range(ny):
                for j in range(nx):
                    cell = np.array([ymin + dy * j + .5 * dy, xmin + dx * i + .5 * dx])
                    self.grid[i][j] = k.predict(cell)
        else:
            print 'method is not supported'
        
        output = demjson.encode({"raster":self.grid})
        self.array_string_out.setValue(output)

        
        
