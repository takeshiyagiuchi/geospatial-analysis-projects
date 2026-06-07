# **********************************************************************
# **********************************************************************
# Script:   sensitivity.py
# Purpose:  Apply a high-level test of the Adirondak trail cost MCE to
#           reasonable changes in criteria weights.
# Name:     Takeshi Yagiuchi
# Date:     November 14, 2025
# **********************************************************************
# **********************************************************************

# C:\Users\tyagiuch>"C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\propy.bat" C:\GEOG6480\Lab03p4\sensitivity.py

import arcpy
from arcpy.sa import Raster

print("Accessing ArcGIS Pro...")
arcpy.CheckOutExtension("Spatial")

print("Setting environment valiables...")
print(arcpy.ListEnvironments())
arcpy.env.workspace = r"C:\GEOG6480\Lab03p4\Lab03p4.gdb"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 18N")
arcpy.env.extent = arcpy.env.workspace + r"\USGS_DEM_Clip_UTM18N"
arcpy.env.cellSize = arcpy.env.workspace + r"\USGS_DEM_Clip_UTM18N"
arcpy.env.mask = arcpy.env.workspace + r"\ReclassedSlop"
arcpy.env.snapRaster = arcpy.env.workspace + r"\USGS_DEM_Clip_UTM18N"

arcpy.env.overwriteOutput = True

print("Setting senario variables...")
suit_mask = arcpy.env.workspace + r"\ReclassedSlop"
transformed_slop = arcpy.env.workspace + r"\Transformed_SlopePercent"
transformed_elev = arcpy.env.workspace + r"\Transformed_USGS_DEM_Clip_UTM18N"
transformed_view = arcpy.env.workspace + r"\Transformed_Viewshed"

weight_slop = 0.55
weight_elev = 0.12
weight_view = 0.33

scenarios_list: list[str] = ["Slope", "Elevation", "Viewshed"]
num_scenarios: int = 0

tmp_weight_slop = 0.0
tmp_weight_elev = 0.0
tmp_weight_view = 0.0

for scenario in scenarios_list:
    print(f"Processing {scenario} scenarios")
    i = 0.01
    while i <= 0.1:
        print(f"Weight + {i}")
        if scenario == "Slope":
            tmp_weight_slop = weight_slop + i
            tmp_weight_elev = weight_elev - (i/2)
            tmp_weight_view = weight_view - (i/2)
        if scenario == "Elevation":
            tmp_weight_slop = weight_slop - (i/2)
            tmp_weight_elev = weight_elev + i
            tmp_weight_view = weight_view - (i/2)
        if scenario == "Viewshed":
            tmp_weight_slop = weight_slop - (i/2)
            tmp_weight_elev = weight_elev - (i/2)
            tmp_weight_view = weight_view + i
        print("Calculating suitability...")
        num_scenarios += 1
        out_raster = arcpy.env.workspace + r"\SensitivityCost" + str(num_scenarios)
        
        tmp_suit_ras = Raster(suit_mask) * (
            (tmp_weight_slop * Raster(transformed_slop)) + 
            (tmp_weight_elev * Raster(transformed_elev)) + 
            (tmp_weight_view * Raster(transformed_view))
        )
        tmp_suit_ras.save(out_raster)
        
        i += 0.01

print("All done!!")
