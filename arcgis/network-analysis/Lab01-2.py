import arcpy

# Define variables
lab01_gdb = r"C:\GEOG3440\Lab01\Lab01.gdb"
fd_streets_name = "Streets"
fd_streets = f"{lab01_gdb}\\{fd_streets_name}"

# Build the network dataset
arcpy.env.workspace = fd_streets
arcpy.na.BuildNetwork(
    in_network_dataset="TransitNetwork_ND", 
    # {force_full_build}
)


