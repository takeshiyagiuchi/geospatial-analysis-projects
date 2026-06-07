def main():
    try:
        print("Starting met_data workflow...")
        input_file = "c_met/data/Rondeau_met_data.csv"
        output_file = "c_met/out/Rondeau_met_data_hourly.csv"

        with open(output_file, "w") as outfile:
            with open(input_file, "r") as infile:
                lines = infile.readlines()
                total_temp = 0.0
                temp_count = 0
                prev_precip = 0.0  # total number of tips that have counted by the start of current hour
                total_precip = 0.0  # Current total number of tips since the log started
                line_num = 0
                prev_hour = "8/5/09 12:00:00 PM"
                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) >= 4: # Ensure there are enough columns
                        if line_num > 1: # Skip  header line
                            if len(parts[2]) > 0: # Temperature value exists
                                total_temp += float(parts[2])
                                temp_count += 1
                            if len(parts[3]) > 0:  # Precipitation value exists
                                total_precip = float(parts[3])  # not hourly but through the whole log
                        if ":00:00" in parts[1] and not prev_hour in parts[1]:
                            # Output the previous hour's data
                            avg_temp = total_temp / temp_count
                            # The precipitation unit is the number of tips.
                            # In precip calculation, we suppose that a tip is immediately
                            # filled at the time when it is counted (though it takes a while in reality).
                            outfile.write(f"{prev_hour},{avg_temp:.2f},{total_precip - prev_precip:.2f}\n")
                            # Reset for the new hour
                            total_temp = 0.0
                            temp_count = 0
                            prev_precip = total_precip
                            prev_hour = parts[1]

                    line_num += 1


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Workflow complete.")

main()