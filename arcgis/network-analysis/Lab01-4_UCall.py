import datetime
from typing import Literal

import arcpy

# Define variables
lab01_gdb = r"C:\GEOG3440\Lab01\Lab01.gdb"
fd_streets_name = "Streets"
fd_streets = f"{lab01_gdb}\\{fd_streets_name}"

def run_service_area_analysis(
    network_data_source: str, 
    layer_name: str, 
    public_transit_time: arcpy.nax.TravelMode, 
    travel_direction: Literal["FROM_FACILITIES", "TO_FACILITIES"], 
    cutoffs: list[int], 
    time_of_day: datetime.datetime, 
    geometry_at_overlaps: Literal["OVERLAP", "DISSOLVE", "SPLIT"], 
    facilities: str, 
) -> None:
    # Create a new service area layer.
    sa_object = arcpy.na.MakeServiceAreaAnalysisLayer(
        network_data_source=network_data_source, 
        layer_name=layer_name, 
        travel_mode=public_transit_time, 
        travel_direction=travel_direction, 
        cutoffs=cutoffs, 
        time_of_day=time_of_day, 
        # {time_zone}, 
        output_type="POLYGONS", 
        # {polygon_detail}, 
        geometry_at_overlaps=geometry_at_overlaps, 
        geometry_at_cutoffs="DISKS", 
        # {polygon_trim_distance}, 
        # {exclude_sources_from_polygon_generation}, 
        # {accumulate_attributes}, 
        # {ignore_invalid_locations}
    )
    
    # Get the layer object from the result object. The service area layer can
    # now be referenced using the layer object.
    sa_layer_object = sa_object.getOutput(0)
    
    # Get the names of all the sublayers within the service area layer.
    sa_sublayer_names = arcpy.na.GetNAClassNames(sa_layer_object)

    # Stores the layer names that we will use later.
    facilities_layer_name = sa_sublayer_names["Facilities"]

    # Load the fire stations as facilities.
    arcpy.na.AddLocations(
        in_network_analysis_layer=sa_layer_object, 
        sub_layer=facilities_layer_name, 
        in_table=facilities, 
        # {field_mappings}, 
        # {search_tolerance}, 
        # {sort_field}, 
        # {search_criteria}, 
        # {match_type}, 
        # {append}, 
        # {snap_to_position_along_network}, 
        # {snap_offset}, 
        # {exclude_restricted_elements}, 
        # {search_query}, 
        # {allow_auto_relocate}
    )

    # Run service area analysis with facilities.
    arcpy.na.Solve(
        sa_layer_object, 
        # ignore_invalids="SKIP", 
        # terminate_on_solve_error="TERMINATE"
    )

    # Save the service area analysis result
    arcpy.management.SaveToLayerFile(
        in_layer=sa_layer_object,
        out_layer=f"{layer_name}.lyrx",
    )
    
    return None

# ### Part2's service area analysis (UC - all) ### #
arcpy.env.workspace = fd_streets

# Import facilities (Great American Ballpark).
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features=r"C:\GEOG3440\Lab01\Facilities\UofGUC.shp", 
    Output_Geodatabase=fd_streets
)

# Set the public transit time.
network_data_source="TransitNetwork_ND"
modes = arcpy.na.GetTravelModes(network_data_source)
public_transit_time = modes["Public transit time"] 

# Run service area analysis for 15, 30, 45 and 60 minutes.
run_service_area_analysis(
    network_data_source=network_data_source, 
    layer_name="SA_toUofGUC_Wed1000", 
    public_transit_time=public_transit_time, 
    travel_direction="TO_FACILITIES", 
    cutoffs=[60, 45, 30, 15], 
    time_of_day=datetime.datetime(2024, 5, 15, 10, 0, 0),  # Wednesday 10:00 AM 
    geometry_at_overlaps="OVERLAP",
    facilities="UofGUC", 
)

# ### Part2's service area analysis (UC - all) ### #
arcpy.env.workspace = fd_streets

# Import facilities (Great American Ballpark).
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features=r"C:\GEOG3440\Lab01\Facilities\UofGUC.shp", 
    Output_Geodatabase=fd_streets
)

# Set the public transit time.
network_data_source="TransitNetwork_ND"
modes = arcpy.na.GetTravelModes(network_data_source)
public_transit_time = modes["Public transit time"] 


network_data_source=network_data_source, 
layer_name="SA_toUofGUC_Wed1000", 
public_transit_time=public_transit_time, 
travel_direction="TO_FACILITIES", 
cutoffs=[60, 45, 30, 15], 
time_of_day=datetime.datetime(2024, 5, 15, 10, 0, 0),  # Wednesday 10:00 AM 
geometry_at_overlaps="OVERLAP",
facilities="UofGUC", 

# Create a new service area layer.
sa_object = arcpy.na.MakeServiceAreaAnalysisLayer(
    network_data_source=network_data_source, 
    # layer_name=layer_name, 
    # travel_mode=public_transit_time, 
    # travel_direction=travel_direction, 
    # cutoffs=cutoffs, 
    # time_of_day=time_of_day, 
    # time_zone="LOCAL_TIME_AT_LOCATIONS", 
    # output_type="POLYGONS", 
    # polygon_detail="STANDARD", 
    # geometry_at_overlaps=geometry_at_overlaps, 
    # geometry_at_cutoffs="DISKS", 
    # # {polygon_trim_distance}, 
    # {exclude_sources_from_polygon_generation}, 
    # {accumulate_attributes}, 
    # {ignore_invalid_locations}
)

# Get the layer object from the result object. The service area layer can
# now be referenced using the layer object.
sa_layer_object = sa_object.getOutput(0)

# Get the names of all the sublayers within the service area layer.
sa_sublayer_names = arcpy.na.GetNAClassNames(sa_layer_object)

# Stores the layer names that we will use later.
facilities_layer_name = sa_sublayer_names["Facilities"]

# Load the fire stations as facilities.
arcpy.na.AddLocations(
    in_network_analysis_layer=sa_layer_object, 
    sub_layer=facilities_layer_name, 
    in_table=facilities, 
    # {field_mappings}, 
    # {search_tolerance}, 
    # {sort_field}, 
    # {search_criteria}, 
    # {match_type}, 
    # {append}, 
    # {snap_to_position_along_network}, 
    # {snap_offset}, 
    # {exclude_restricted_elements}, 
    # {search_query}, 
    # {allow_auto_relocate}
)

# # Run service area analysis with facilities.
# arcpy.na.Solve(
#     sa_layer_object, 
#     # ignore_invalids="SKIP", 
#     # terminate_on_solve_error="TERMINATE"
# )

# # Save the service area analysis result
# arcpy.management.SaveToLayerFile(
#     in_layer=sa_layer_object,
#     out_layer=f"{layer_name}.lyrx",
# )

# Import marginalization data.
arcpy.env.workspace = fd_streets
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features=r"C:\GEOG3440\GEOG3440_F24_Lab01_GuelphMarg\GuelphMarg.shp", 
    Output_Geodatabase=fd_streets
)



