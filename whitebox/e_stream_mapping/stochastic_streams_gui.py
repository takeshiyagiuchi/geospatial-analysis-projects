from tkinter import *
from tkinter import filedialog, ttk
import random

import whitebox_workflows

class Window(Frame):

    def __init__(self, master=None):
        ###################################
        # This is where we create our GUI #
        ###################################

        Frame.__init__(self, master)        
        self.master = master

        # DEM file name
        dem_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        dem_label = Label(dem_frame, text="DEM file name:")
        dem_label.grid(column = 0, row = 0, sticky=W)
        self.dem_file_name = StringVar()
        dem_entry = Entry(dem_frame, width=40, textvariable=self.dem_file_name)
        dem_entry.grid(column = 1, row = 0, sticky=E)
        dem_button = Button(dem_frame, text="...", command=self.dem_file_selector)
        dem_button.grid(column = 2, row = 0)
        dem_frame.grid_columnconfigure(1, weight=1)
        dem_frame.grid(column = 0, row = 0, sticky=W+E) # First row of widgets


        # Number of iterations
        iter_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        iter_label = Label(iter_frame, text="Number of iterations:")
        iter_label.grid(column = 0, row = 0, sticky=W)
        self.num_iter = StringVar(value='1000') # Set default
        iter_entry = Entry(iter_frame, width=12, justify=RIGHT, textvariable=self.num_iter)
        iter_entry.grid(column = 1, row = 0, sticky=E)
        iter_frame.grid_columnconfigure(1, weight=1)
        iter_frame.grid(column = 0, row = 1, sticky=W+E) # Second row of widgets


        # DEM RMSE
        dem_rmse_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        dem_rmse_label = Label(dem_rmse_frame, text="DEM root-mean-square-error (RMSE):")
        dem_rmse_label.grid(column = 0, row = 0, sticky=W)
        self.dem_rmse = StringVar(value='5.0') # Set default
        dem_rmse_entry = Entry(dem_rmse_frame, width=12, justify=RIGHT, textvariable=self.dem_rmse)
        dem_rmse_entry.grid(column = 1, row = 0, sticky=E)
        dem_rmse_frame.grid_columnconfigure(1, weight=1)
        dem_rmse_frame.grid(column = 0, row = 2, sticky=W+E) # Third row of widgets


        # DEM error spatial autocorrelation length
        dem_autocor_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        dem_autocor_label = Label(dem_autocor_frame, text="DEM error spatial autocorrelation length (m):")
        dem_autocor_label.grid(column = 0, row = 0, sticky=W)
        self.dem_autocor = StringVar(value='75.0') # Set default
        dem_autocor_entry = Entry(dem_autocor_frame, width=12, justify=RIGHT, textvariable=self.dem_autocor)
        dem_autocor_entry.grid(column = 1, row = 0, sticky=E)
        dem_autocor_frame.grid_columnconfigure(1, weight=1)
        dem_autocor_frame.grid(column = 0, row = 3, sticky=W+E) # Fourth row of widgets


        # Stream threshold
        stream_threshold_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        stream_threshold_label = Label(stream_threshold_frame, text="Stream area threshold (cells):")
        stream_threshold_label.grid(column = 0, row = 0, sticky=W)
        self.stream_threshold = StringVar(value='500.0') # Set default
        stream_threshold_entry = Entry(stream_threshold_frame, width=12, justify=RIGHT, textvariable=self.stream_threshold)
        stream_threshold_entry.grid(column = 1, row = 0, sticky=E)
        stream_threshold_frame.grid_columnconfigure(1, weight=1)
        stream_threshold_frame.grid(column = 0, row = 4, sticky=W+E) # Fifth row of widgets


        # Stream threshold RMSE
        threshold_rmse_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        threshold_rmse_label = Label(threshold_rmse_frame, text="Stream area threshold RMSE (cells):")
        threshold_rmse_label.grid(column = 0, row = 0, sticky=W)
        self.threshold_rmse = StringVar(value='25.0') # Set default
        threshold_rmse_entry = Entry(threshold_rmse_frame, width=12, justify=RIGHT, textvariable=self.threshold_rmse)
        threshold_rmse_entry.grid(column = 1, row = 0, sticky=E)
        threshold_rmse_frame.grid_columnconfigure(1, weight=1)
        threshold_rmse_frame.grid(column = 0, row = 5, sticky=W+E) # Sixth row of widgets


        # Output file name
        output_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        output_label = Label(output_frame, text="Output file name:")
        output_label.grid(column = 0, row = 0, sticky=W)
        self.output_file_name = StringVar()
        output_entry = Entry(output_frame, width=40, textvariable=self.output_file_name)
        output_entry.grid(column = 1, row = 0, sticky=E)
        output_button = Button(output_frame, text="...", command=self.output_file_selector)
        output_button.grid(column = 2, row = 0)
        output_frame.grid_columnconfigure(1, weight=1)
        output_frame.grid(column = 0, row = 6, sticky=W+E) # Seventh row of widgets


        bottom_frame = Frame(master, padx=10, pady=10)

        # Exit and OK buttons
        btn_frame = Frame(bottom_frame)
        ok_btn = Button(btn_frame, text="OK", command=self.run_stochastic_streams)
        ok_btn.grid(column=0, row=0, sticky=W)
        exit_btn = Button(btn_frame, text='Exit', command=self.exit)
        exit_btn.grid(column=1, row=0, sticky=W)
        btn_frame.grid(column=0, row=8, sticky=W) # Ninth row of widgets

        # Add a progress label and bar
        progress_frame = Frame(bottom_frame)
        self.progress_label = StringVar(value='Progress: ')
        progress_label = Label(progress_frame, textvariable=self.progress_label)
        progress_label.grid(column=0, row=0) #, sticky=W)
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', length=200)
        self.progress_bar.grid(column=1, row=0) #, sticky=W)
        progress_frame.grid(column=1, row=8, sticky=E) # Shared with btn_frame in the ninth row of widgets

        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid(column=0, row=8, sticky=W+E)
        
 
    # The method in which we run our model. This is called when we press the 'OK' button.
    def run_stochastic_streams(self):

        try:
            # Retrieve the parameters from the GUI
            dem_file = self.dem_file_name.get() # Notice I use the 'get()' method of StrVar to retrieve the string in the entry box
            num_iter = int(self.num_iter.get()) # Have to convert the string to an integer
            dem_rmse = float(self.dem_rmse.get())
            dem_autocor = float(self.dem_autocor.get())
            stream_threshold = float(self.stream_threshold.get())
            threshold_rmse = float(self.threshold_rmse.get())
            output_file = self.output_file_name.get()

            # Set up the WbEnvironment
            wbe = whitebox_workflows.WbEnvironment()

            try:
                # Here we run the model with the user input parameters. This is the 
                # same code from before, we've just updated the parameter variable
                # names instead of using the default_parameter[] list.

                dem = wbe.read_raster(dem_file)

                filter_size = dem_autocor / dem.configs.resolution_x / 3.0

                streams_freq = wbe.new_raster(dem.configs)
                streams_freq.reinitialize_values(0.0)

                old_progress = -1
                for i in range(num_iter): # iterate as many times as requested
                    # Create an error model realization
                    random_grid = wbe.random_field(dem)
                    random_grid_sa = wbe.fast_almost_gaussian_filter(random_grid, filter_size)
                    (mean, sd) = random_grid_sa.calculate_mean_and_stdev()
                    random_grid_sa_freq_dist = (random_grid_sa - mean) * dem_rmse / sd
                    
                    # Add the error field to the DEM to create a realization
                    dem_error_added = dem + random_grid_sa_freq_dist

                    # Extract a stream network from my error-added DEM
                    dem_filled = wbe.fill_depressions_wang_and_liu(dem_error_added, fix_flats=True, flat_increment=0.001)

                    flow_accum = wbe.d8_flow_accum(dem_filled, out_type='cells', log_transform=False)

                    streams = flow_accum > stream_threshold + random.gauss(0.0, threshold_rmse)

                    streams_freq += streams

                    progress = int((i+1) / num_iter * 100.0)
                    if progress != old_progress:
                        self.update_progress(f"Progress: {progress}%", progress)
                        old_progress = progress

                
                # Calculate stream probability here...
                stream_prob = streams_freq / num_iter

                # output final raster
                wbe.write_raster(stream_prob, output_file, True)

                self.update_progress("Progress:", 0) # reset the progress

                print("Calculation complete")

            except Exception as e:
                print("The error raised is: ", e)

        except Exception as e:
                print("Error reading a model parameter or creating the WbEnvironment: ", e)

        finally:
            print("All Done!")

    # A method for updating the progress label and bar
    def update_progress(self, label, progress):
        self.progress_label.set(label) # update the progress
        self.progress_bar['value'] = progress
        self.master.update()

    def exit(self):
        exit(0)

    def dem_file_selector(self):
        fn = filedialog.askopenfilename(title='Select the DEM file')
        self.dem_file_name.set(fn)

    def output_file_selector(self):
        fn = filedialog.asksaveasfilename(title='Save As')
        self.output_file_name.set(fn)

        
root = Tk()
app = Window(root)
root.wm_title("Stochastic Streams")
root.mainloop()