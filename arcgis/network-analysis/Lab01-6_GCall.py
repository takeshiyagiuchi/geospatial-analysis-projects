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

# ### Part3's service area analysis (GC - all) ### #
arcpy.env.workspace = fd_streets

# Import facilities (Great American Ballpark).
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features=r"C:\GEOG3440\GEOG3440_F24_Lab01_GuelphMarg\GuelphGroceries.shp", 
    Output_Geodatabase=fd_streets
)

# Set the public transit time.
network_data_source="TransitNetwork_ND"
modes = arcpy.na.GetTravelModes(network_data_source)
public_transit_time = modes["Public transit time"] 

# Run service area analysis for 10 and 20 minutes.
layer_name = "SA_toGroceries_Wed1400"
run_service_area_analysis(
    network_data_source=network_data_source, 
    layer_name=layer_name, 
    public_transit_time=public_transit_time, 
    travel_direction="TO_FACILITIES", 
    cutoffs=[10, 20], 
    time_of_day=datetime.datetime(2024, 5, 15, 14, 0, 0),  # Wednesday 14:00 AM 
    geometry_at_overlaps="DISSOLVE",
    facilities="GuelphGroceries", 
)

arcpy.env.workspace = lab01_gdb
layer_dissolved_name = f"{layer_name}_dissolved"
arcpy.management.Dissolve(
    in_features=f"{layer_name}\\Polygons", 
    out_feature_class=layer_dissolved_name, 
    dissolve_field="ToBreak", 
    # {statistics_fields}, 
    multi_part="MULTI_PART", 
    # {unsplit_lines}, 
    # {concatenation_separator}
)

# Import marginalization data.
arcpy.env.workspace = fd_streets
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features=r"C:\GEOG3440\GEOG3440_F24_Lab01_GuelphMarg\GuelphMarg.shp", 
    Output_Geodatabase=fd_streets
)

# Add the area field.
fl_marg = "GuelphMarg"
field_area_old = "AreaOrig_Ha"
arcpy.management.AddField(
    in_table=fl_marg, 
    field_name=field_area_old, 
    field_type="DOUBLE", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
arcpy.management.CalculateGeometryAttributes(
    in_features=fl_marg, 
    geometry_property=[[field_area_old, "AREA"]], 
    # {length_unit}, 
    area_unit="HECTARES", 
    # {coordinate_system}, 
    # {coordinate_format}
)

# Union marginalization data and service area layer
fc_union = "Union_Marg_SA"
arcpy.analysis.Union(
    in_features=[[fl_marg, ""], [layer_dissolved_name, ""]], 
    out_feature_class=fc_union, 
    # {join_attributes}, 
    # {cluster_tolerance}, 
    # {gaps}
)

# Add a new area field.
field_area_new = "AreaNew_Ha"
arcpy.management.AddField(
    in_table=fc_union, 
    field_name=field_area_new, 
    field_type="DOUBLE", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
arcpy.management.CalculateGeometryAttributes(
    in_features=fc_union, 
    geometry_property=[[field_area_new, "AREA"]], 
    # {length_unit}, 
    area_unit="HECTARES", 
    # {coordinate_system}, 
    # {coordinate_format}
)

# Add a scaled population field.
field_pop_scaled = "PopScaled"
arcpy.management.AddField(
    in_table=fc_union, 
    field_name=field_pop_scaled, 
    field_type="DOUBLE", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
arcpy.management.CalculateField(
    in_table=fc_union, 
    field=field_pop_scaled, 
    expression=f"0 if !{field_area_old}! == 0 else !Pop2021! * !{field_area_new}! / !{field_area_old}!", 
    expression_type="PYTHON3", 
    # {code_block}, 
    # {field_type}, 
    # {enforce_domains}
)

# Add a weighted marginalization field.
field_marg_weighted = "MargWeighted"
arcpy.management.AddField(
    in_table=fc_union, 
    field_name=field_marg_weighted, 
    field_type="DOUBLE", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
arcpy.management.CalculateField(
    in_table=fc_union, 
    field=field_marg_weighted, 
    expression=f"!AvgMarg! * !{field_pop_scaled}!", 
    expression_type="PYTHON3", 
    # {code_block}, 
    # {field_type}, 
    # {enforce_domains}
)

# Summarize the results
summary_table = f"{lab01_gdb}\\SA_Marg_Summary"
field_marg_final = "AveMargFinal"
arcpy.analysis.Statistics(
    in_table=fc_union, 
    out_table=summary_table, 
    statistics_fields=[
        [field_pop_scaled, "SUM"],
        [field_marg_weighted, "SUM"]
    ], 
    case_field="ToBreak", 
    # {concatenation_separator}
)
arcpy.management.AddField(
    in_table=summary_table, 
    field_name=field_marg_final, 
    field_type="DOUBLE", 
    # {field_precision}, 
    # {field_scale}, 
    # {field_length}, 
    # {field_alias}, 
    # {field_is_nullable}, 
    # {field_is_required}, 
    # {field_domain}
)
arcpy.management.CalculateField(
    in_table=summary_table, 
    field=field_marg_final, 
    expression=f"!SUM_{field_marg_weighted}! / !SUM_{field_pop_scaled}!", 
    expression_type="PYTHON3", 
    # {code_block}, 
    # {field_type}, 
    # {enforce_domains}
)


