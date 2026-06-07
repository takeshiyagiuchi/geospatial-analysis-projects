# Import Necessary packages and methods
import arcpy
from arcpy.conversion import ConvertLas, LasDatasetToRaster
from arcpy.ia import Hillshade
from arcpy.management import MakeLasDatasetLayer, MosaicToNewRaster

project = arcpy.mp.ArcGISProject("CURRENT")

# Set the workspace directory
arcpy.env.workspace = r"C:\GEOG6480\Lab03\LAZ"

# Set the output coordinate system
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(26917)

# List all the .laz files
laz_list: list[str] = arcpy.ListFiles("*.laz")

# Print out the filenames without extension
for i in laz_list:
    print(i.rstrip(".laz"))

# Convert LAZ to LAS
for laz in laz_list:
    ConvertLas(
        in_las=laz,
        target_folder=r"C:\GEOG6480\Lab03\LAS",
        define_coordinate_system="FILES_MISSING_PROJECTION",
        in_coordinate_system=arcpy.env.outputCoordinateSystem
    )

# Create Raster from LAS
arcpy.env.workspace = r"C:\GEOG6480\Lab03\LAS"
las_list: list[str] = arcpy.ListFiles("*.las")
for i, las in enumerate(las_list):
    print(f"{i + 1}/{len(las_list)}: {las}")
    layer_name: str = las.rstrip(".las")
    MakeLasDatasetLayer(
        in_las_dataset=las, 
        out_layer=layer_name
    )
    LasDatasetToRaster(
        in_las_dataset=layer_name, 
        out_raster=f"C:\\GEOG6480\\Lab03\\Lab03.gdb\\a{las.rstrip('.las')}", 
        interpolation_type="BINNING AVERAGE LINEAR", 
        data_type="FLOAT", 
        sampling_type="CELLSIZE", 
        sampling_value=0.5
    )
    arcpy.management.Delete(layer_name)

print("Move on to the mosaic and hillshade stage...")

# Set the geodatabase as workspace
arcpy.env.workspace = r"C:\GEOG6480\Lab03\Lab03.gdb"
print(f"Current work space: {arcpy.env.workspace}")

# List out all the DSM rasters
dsm_rasters_list: list[str] = arcpy.ListRasters("a1km*")
for i in dsm_rasters_list:
    print(i)

# Put all the sectional raster together
MosaicToNewRaster(
    input_rasters=dsm_rasters_list, 
    output_location=arcpy.env.workspace, 
    raster_dataset_name_with_extension="HumberBayMozaic", 
    # {coordinate_system_for_the_raster}, 
    # {pixel_type}, 
    # {cellsize}, 
    number_of_bands=1, 
    # {mosaic_method}, 
    # {mosaic_colormap_mode}
)

# Add hill shade
Hillshade(
    dem="HumberBayMozaic", 
    azimuth=175.26, 
    altitude=45.98, 
    # {z_factor}, 
    # {slope_type}, 
    # {ps_power}, 
    # {psz_factor}, 
    # {remove_edge_effect}, 
    # {hillshade_type}
)

# Add hill shade
out_hillshade_raster = Hillshade(
    dem="HumberBayMozaic", 
    azimuth=175.26, 
    altitude=45.98, 
    # {z_factor}, 
    # {slope_type}, 
    # {ps_power}, 
    # {psz_factor}, 
    # {remove_edge_effect}, 
    # {hillshade_type}
)
out_hillshade_raster.save(r"C:\GEOG6480\Lab03\hillshade2.tif")

# Save changes
project.save()
print("Complete!")

# Part 3 - Sensitivity/Robustness Analysis
print("Part3")
filename_mosaic_root: str = "HumberBayMozaic"

for i in [3, 5, 7, 9]:
    kernel_width: int = i
    kernel_height: int  = i
    kernel = arcpy.sa.NbrRectangle(kernel_width, kernel_height, "CELL")
    
    # Focal Statistics
    print(f"Focal Statistics {i}x{i} ...")
    std_filter = arcpy.sa.FocalStatistics(
        in_raster=filename_mosaic_root, 
        neighborhood=kernel, 
        statistics_type="STD", 
        ignore_nodata="DATA", 
        # {percentile_value}
    )
    filename_mosaic_fs: str = f"{filename_mosaic_root}FS{i}x{i}"
    std_filter.save(filename_mosaic_fs)
    
    # Conditional Analysis
    print(f"Conditional Analysis {i}x{i} ...")
    out_con = arcpy.sa.Con(
        in_conditional_raster=filename_mosaic_fs, 
        in_true_raster_or_constant=1, 
        # {in_false_raster_or_constant}, 
        where_clause="VALUE > 2.5"
    )
    filename_mosaic_con: str = f"{filename_mosaic_root}Con{i}x{i}"
    out_con.save(filename_mosaic_con)

    # Raster to Polygon
    print(f"Raster to Polygon {i}x{i} ...")
    arcpy.conversion.RasterToPolygon(
        in_raster=filename_mosaic_con, 
        out_polygon_features=f"{filename_mosaic_root}PG{i}x{i}", 
        simplify="NO_SIMPLIFY", 
        raster_field = "VALUE", 
        # {create_multipart_features}, 
        # {max_vertices_per_feature}
    )


