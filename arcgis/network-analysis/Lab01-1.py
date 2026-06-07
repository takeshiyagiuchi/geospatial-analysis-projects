# Setup
#  - Create a project named "Lab01" under r"C:\GEOG3440".
#  - Download Network Data Set, 2023, published by DMTI Spatial Inc. 
#    from Scholar’s Geoportal.
#  - Place the extracted folder under r"C:\GEOG3440"

import arcpy

# Define the path to Lab01 gdb
lab01_gdb = r"C:\GEOG3440\Lab01\Lab01.gdb"

# Validate paths
if not arcpy.Exists(lab01_gdb):
    raise FileNotFoundError(f"Main geodatabase not found: {lab01_gdb}")

arcpy.env.workspace = lab01_gdb

# Import the GTFS datum
path_gtfs = r"C:\GEOG3440\GEOG3440_F24_Lab01_GuelphGTFS"
fd_streets_name = "Streets"
fd_streets = f"{lab01_gdb}\\{fd_streets_name}"

arcpy.management.CreateFeatureDataset(
    out_dataset_path=lab01_gdb, 
    out_name=fd_streets_name, 
    spatial_reference=arcpy.SpatialReference(26917)  # EPSG for NAD83 / UTM zone 17N
)

arcpy.transit.GTFSToPublicTransitDataModel(
    in_gtfs_folders=[path_gtfs], 
    target_feature_dataset=fd_streets, 
    # {interpolate}, 
    # {append}, 
    # {make_lve_shapes}
)

# Define the path to DMTI 2023 gdb
external_gdb = r"C:\GEOG3440\DMTI_2023_CMCS_NetworkDataSet\data\DMTI_2023_CMCS_NetworkDataSet.gdb\Network"

# Validate paths
if not arcpy.Exists(external_gdb):
    raise FileNotFoundError(f"External geodatabase not found: {external_gdb}")

# List all feature classes in the external geodatabase
arcpy.env.workspace = external_gdb
feature_classes = arcpy.ListFeatureClasses()

for fc in feature_classes:
    print(fc)

# Import the RoadsNetwork feature class as a feature layer
fc_roads_network = r"C:\GEOG3440\DMTI_2023_CMCS_NetworkDataSet\data\DMTI_2023_CMCS_NetworkDataSet.gdb\Network\RoadsNetwork"
fl_roads_network = "RoadsNetwork"
arcpy.management.MakeFeatureLayer(
    in_features=fc_roads_network, 
    out_layer=fl_roads_network, 
    # {where_clause}, 
    # {workspace}, 
    # {field_info}
)

arcpy.env.workspace = fd_streets

# Filter the roads in Guelph
fl_roads_network_guelph_tmp = "RoadsNetworkGuelphTmp"
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=fl_roads_network, 
    selection_type="NEW_SELECTION", 
    where_clause="LEFT_MAF = 'GUELPH'", 
    # {invert_where_clause}
)

# Make a feature class from the selected layer
arcpy.management.CopyFeatures(
    in_features=fl_roads_network, 
    out_feature_class=fl_roads_network_guelph_tmp, 
    # {config_keyword}, 
    # {spatial_grid_1}, 
    # {spatial_grid_2}, 
    # {spatial_grid_3}
)

# Add a ROAD_CLASS field to Streets to use template
arcpy.management.AddField(
    in_table=fl_roads_network_guelph_tmp, 
    field_name="ROAD_CLASS", 
    field_type="SHORT", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)

# Add a RestrictPedestrians field to Streets to use template
arcpy.management.AddField(
    in_table=fl_roads_network_guelph_tmp, 
    field_name="RestrictPedestrians", 
    field_type="TEXT", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
with arcpy.da.UpdateCursor(
    fl_roads_network_guelph_tmp, 
    ("STREET", "RestrictPedestrians")
) as cursor:
    for row in cursor:
        if row[0] == "HANLON PKY":
            row[1] = "Y" 
        else:
            row[1] = "N"
        cursor.updateRow(row)


# Change the coordinate system
fl_roads_network_guelph = "Streets"  # The feature class name has to be "Streets" to use template later
arcpy.management.Project(
    in_dataset=fl_roads_network_guelph_tmp, 
    out_dataset=fl_roads_network_guelph, 
    out_coor_system=arcpy.SpatialReference(26917),  # the EPSG/WKID for NAD 1983 / UTM Zone 17N
    # {transform_method}, 
    # {in_coor_system}, 
    # {preserve_shape}, 
    # {max_deviation}, 
    # {vertical}
)

# Delete the temporary feature class and layer
arcpy.Delete_management(fl_roads_network)
arcpy.Delete_management(f"{fd_streets}\\{fl_roads_network_guelph_tmp}")
arcpy.Delete_management(fl_roads_network_guelph_tmp)

# Recreate the feature layer
arcpy.management.MakeFeatureLayer(
    in_features=fl_roads_network_guelph, 
    out_layer=fl_roads_network_guelph, 
    # {where_clause}, 
    # {workspace}, 
    # {field_info}
)

# Connect the transit stops to the streets
arcpy.env.workspace = lab01_gdb
arcpy.transit.ConnectPublicTransitDataModelToStreets(
    target_feature_dataset=fd_streets_name, 
    in_streets_features=fl_roads_network_guelph, 
    search_distance=375, # We need 375 meters to connect all the points
    expression="RestrictPedestrians <> 'Y'"
)

# Create the network dataset from a template
arcpy.na.CreateNetworkDatasetFromTemplate(
    network_dataset_template=r"C:\GEOG3440\Network_Analyst_Pro_Tutorial\Network Analyst\Tutorial\PublicTransit\TransitNetworkTemplate.xml", 
    output_feature_dataset=fd_streets_name
)

# You have to modify the property manually here.
# (Seems like there is no way to edit the network dataset properties
# with arcpy.)
