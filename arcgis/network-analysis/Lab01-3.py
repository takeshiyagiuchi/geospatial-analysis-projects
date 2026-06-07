import datetime
from typing import Literal

import arcpy

# Define variables
lab01_gdb = r"C:\GEOG3440\Lab01\Lab01.gdb"
fd_streets_name = "Streets"
fd_streets = f"{lab01_gdb}\\{fd_streets_name}"

# Create a shapefile for U of G University Center
arcpy.env.workspace = lab01_gdb
arcpy.management.CopyFeatures(
    in_features=r"SA-toUofGUC-Wed1000\Facilities", 
    out_feature_class="UofGUC", 
    # {config_keyword}, 
    # {spatial_grid_1}, 
    # {spatial_grid_2}, 
    # {spatial_grid_3}
)
arcpy.conversion.FeatureClassToShapefile(
    Input_Features="UofGUC", 
    Output_Folder=r"C:\GEOG3440\Lab01\Facilities"
)
