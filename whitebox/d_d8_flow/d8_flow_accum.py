from math import sqrt
from whitebox_workflows import WbEnvironment


def main():
    try:
        wbe = WbEnvironment()
        wbe.verbose = False
        wbe.working_directory = input("Please enter the working directory: ")
        input_dem = input("Please enter the name of the input DEM: ")
        output_raster = input("Please enter the name of the output flow accumulation raseter: ")
        log_transform = input("Do you want to log-transform the output? (Y or n)")

        dem = wbe.read_raster(input_dem)
        dem_filled = wbe.fill_depressions_wang_and_liu(dem)  # pre-processing to remove depressions

        rows = dem_filled.configs.rows
        columns = dem_filled.configs.columns
        nodata = dem_filled.configs.nodata
        res_x = dem_filled.configs.resolution_x
        res_y = dem_filled.configs.resolution_y
        res_diag = sqrt(res_x * res_x + res_y * res_y)

        dx = (1, 1, 1, 0, -1, -1, -1, 0)
        dy = (-1, 0, 1, 1, 1, 0, -1, -1)
        dist = (res_diag, res_x, res_diag, res_y, res_diag, res_x, res_diag, res_y)

        flow_dir_raster = wbe.new_raster(dem.configs)

        print("\nCalculating flow directions...")
        prev_progress = -1
        # Visit every grid cell and find the downslope neighbour
        for row in range(0, rows):
            for col in range(0, columns):
                z = dem_filled[row, col]
                if z != nodata:
                    # Visit every neighbour
                    slope = 0.0
                    flow_n = -1
                    for n in range(0, 8):
                        zn = dem_filled[row + dy[n], col + dx[n]]
                        if zn != nodata:
                            # calculate the slope!
                            slope_n = (z - zn) / dist[n]
                            if slope_n > slope:
                                slope = slope_n
                                flow_n = n

                    flow_dir_raster[row, col] = flow_n

            progress = int(100.0 * (row + 1) / rows)
            if progress != prev_progress:
                print(f"Progress (1 of 3): {progress}%")
                prev_progress = progress

        # wbe.write_raster(flow_dir_raster, 'd_d8_flow/out/flow_dir.tif', compress=True)

        print("\nCounting number of inflowing neighbours...")
        nin_raster = wbe.new_raster(dem.configs)
        in_fd = (4, 5, 6, 7, 0, 1, 2, 3)
        current_flow_path_cells = []
        prev_progress = -1
        num_valid_cells = 0
        # Visit every grid cell and find the downslope neighbour
        for row in range(0, rows):
            for col in range(0, columns):
                z = dem_filled[row, col]
                if z != nodata:
                    num_valid_cells += 1
                    # Visit every neighbour
                    nin = 0
                    for n in range(0, 8):
                        zn = dem_filled[row + dy[n], col + dx[n]]
                        if zn != nodata:
                            fd = flow_dir_raster[row + dy[n], col + dx[n]]
                            if fd == in_fd[n]:
                                nin += 1

                    nin_raster[row, col] = nin
                    if nin == 0:
                        # I'm at the start of a flow path. Let it rain!
                        current_flow_path_cells.append((row, col))

            progress = int(100.0 * (row + 1) / rows)
            if progress != prev_progress:
                print(f"Progress (2 of 3): {progress}%")
                prev_progress = progress

        # wbe.write_raster(nin_raster, "d_d8_flow/out/nin_raster.tif", compress=True)

        # Perform the flow path accumulation
        flow_accum = wbe.new_raster(dem.configs)
        flow_accum.reinitialize_values(1.0)

        num_cells_solved = 0
        while len(current_flow_path_cells) > 0:
            (row, col) = current_flow_path_cells.pop()
            num_cells_solved += 1
            fd = int(flow_dir_raster[row, col])
            fa = flow_accum[row, col]
            if fd > -1:
                flow_accum[row + dy[fd], col + dx[fd]] += fa

                nin_raster[row + dy[fd], col + dx[fd]] -= 1
                if nin_raster[row + dy[fd], col + dx[fd]] == 0:
                    current_flow_path_cells.append((row + dy[fd], col + dx[fd]))

            progress = int(num_cells_solved / num_valid_cells * 100)
            if progress != prev_progress:
                print(f"Progress (3 of 3): {progress}%")
                prev_progress = progress

        if "y" in log_transform.lower():
            flow_accum = flow_accum.ln()

        wbe.write_raster(flow_accum, output_raster, compress=True)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Workflow complete.")

main()
