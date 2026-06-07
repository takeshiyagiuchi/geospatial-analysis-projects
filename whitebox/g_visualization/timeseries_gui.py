# --- For Assignment 3 ---
# In addition to the input file path and output path,
# I also implemented plot line color selection in the GUI interface.
# I chose colors as additional input options because
# supporting all possible CSV file formats would be too complicated,
# and the font path uses the same input style as the other file paths
# in the interface.
# I also added error handling for the color selection and output path.

import re
import warnings
from datetime import datetime
from pathlib import Path
from tkinter import (
    Button, Entry, Frame, Label, StringVar,
    E, W, Tk, filedialog
)

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

# This is a common sequence of colors used for plotting.
COLOR_SEQUENCE = [
    '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
    '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
    '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
    '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5'
]

class Window(Frame):

    def __init__(self, master=None):
        ###################################
        # This is where we create our GUI #
        ###################################

        Frame.__init__(self, master)
        self.master = master

        # DEM file name
        dem_frame = Frame(master, padx=10, pady=5)  # Defines the widget group
        dem_label = Label(dem_frame, text="Input file name:")
        dem_label.grid(column=0, row=0, sticky=W)
        self.dem_file_name = StringVar()
        dem_entry = Entry(dem_frame, width=40, textvariable=self.dem_file_name)
        dem_entry.grid(column=1, row=0, sticky=E)
        dem_button = Button(dem_frame, text="...", command=self.dem_file_selector)
        dem_button.grid(column=2, row=0)
        dem_frame.grid_columnconfigure(1, weight=1)
        dem_frame.grid(column=0, row=0, sticky=W + E)  # First row of widgets

        # Color for Temperature
        color_tmp_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        color_tmp_label = Label(color_tmp_frame, text="Color for Temperature:")
        color_tmp_label.grid(column = 0, row = 0, sticky=W)
        self.color_tmp = StringVar(value=COLOR_SEQUENCE[0]) # Set default
        color_tmp_entry = Entry(color_tmp_frame, width=12, justify="right", textvariable=self.color_tmp)
        color_tmp_entry.grid(column = 1, row = 0, sticky=E)
        color_tmp_frame.grid_columnconfigure(1, weight=1)
        color_tmp_frame.grid(column = 0, row = 1, sticky=W+E) # Second row of widgets

        # Color for Precipitation
        color_prc_frame = Frame(master, padx=10, pady=5) # Defines the widget group
        color_prc_label = Label(color_prc_frame, text="Color for Precipitation:")
        color_prc_label.grid(column = 0, row = 0, sticky=W)
        self.color_prc = StringVar(value=COLOR_SEQUENCE[2]) # Set default
        color_prc_entry = Entry(color_prc_frame, width=12, justify="right", textvariable=self.color_prc)
        color_prc_entry.grid(column = 1, row = 0, sticky=E)
        color_prc_frame.grid_columnconfigure(1, weight=1)
        color_prc_frame.grid(column = 0, row = 2, sticky=W+E) # Third row of widgets

        # Output file name
        output_frame = Frame(master, padx=10, pady=5)  # Defines the widget group
        output_label = Label(output_frame, text="Output file name:")
        output_label.grid(column=0, row=0, sticky=W)
        self.output_file_name = StringVar()
        output_entry = Entry(output_frame, width=40, textvariable=self.output_file_name)
        output_entry.grid(column=1, row=0, sticky=E)
        output_button = Button(output_frame, text="...", command=self.output_file_selector)
        output_button.grid(column=2, row=0)
        output_frame.grid_columnconfigure(1, weight=1)
        output_frame.grid(column=0, row=3, sticky=W + E)  # Fourth row of widgets

        bottom_frame = Frame(master, padx=10, pady=10)

        # Exit and OK buttons
        btn_frame = Frame(bottom_frame)
        ok_btn = Button(btn_frame, text="OK", command=self.plot_time_series)
        ok_btn.grid(column=0, row=0, sticky=W)
        exit_btn = Button(btn_frame, text='Exit', command=self.exit)
        exit_btn.grid(column=1, row=0, sticky=W)
        btn_frame.grid(column=0, row=4, sticky=W)  # Fifth row of widgets

        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid(column=0, row=4, sticky=W + E)

    # The method in which we run our model. This is called when we press the 'OK' button.
    def plot_time_series(self):

        try:
            # Fonts
            #     fontpath = '/Users/johnlindsay/Library/Fonts/OpenSans-Regular.ttf'
            #     prop = font_manager.FontProperties(fname=fontpath)
            #     matplotlib.rcParams['font.family'] = prop.get_name()
            #     matplotlib.rcParams.update({'font.size': 10})

            # read in the data
            file_name = self.dem_file_name.get()
            col_headers = ("Time", "Temperature", "Precipitation")

            # When reading data containing a date-time, you need to tell it how to parse the date.
            # This is based on the format of the time string in the csv file.
            def convertfunc(x): return datetime.strptime(x, '%m/%d/%y %I:%M:%S %p')

            data = np.genfromtxt(
                file_name,
                delimiter=",",
                skip_header=0,
                names=col_headers,
                dtype=(object, float, float),
                converters={"Time": convertfunc}
            )

            # Check Input colors
            def check_color(color: str):
                return bool(re.fullmatch(r"#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})", color))
            color_tmp = self.color_tmp.get()
            if not check_color(color=color_tmp):
                warnings.warn(f"Input color is not valid: {color_tmp}")
                color_tmp = COLOR_SEQUENCE[0]
            color_prc = self.color_prc.get()
            if not check_color(color=color_prc):
                warnings.warn(f"Input color is not valid: {color_prc}")
                color_prc = COLOR_SEQUENCE[0]

            # Check output path
            output_file_name = self.output_file_name.get().strip()
            if not output_file_name:
                raise ValueError("Output file name is not given")
            output_file_name = Path(output_file_name)
            if not (output_file_name.parent.exists()):
                raise ValueError("The parent directory of output file does not exist")

            # Plot
            fig, (ax1, ax2) = plt.subplots(nrows=2)
            ax1.grid(True, linestyle="dotted", color=(0.5, 0.5, 0.5))
            ax1.plot(
                data['Time'],
                data['Temperature'],
                color=color_tmp,
                label="Temperature",
                marker="o",
                markersize=2
            )
            ax1.set(
                xlabel='Date',
                ylabel='Temperature (Celsius)',
                title='Hourly Temperature'
            )

            ax2.grid(True, linestyle="dotted", color=(0.0, 0.0, 0.0))
            ax2.plot(
                data['Time'],
                data['Precipitation'],
                color=color_prc,
                label="Precip"
            )
            ax2.set(
                xlabel='Date',
                ylabel='Precipitation (mm)',
                title='Hourly Precipitation'
            )

            day_month_fmt = mdates.DateFormatter('%d/%m')
            ax2.xaxis.set_major_formatter(day_month_fmt)
            fig.autofmt_xdate()

            # Set the size...this is really touchy
            fig.set_size_inches(10.0, 4.0, forward=True)

            # Save it to an image file
            filepath_out = self.output_file_name.get()
            plt.savefig(
                filepath_out,
                dpi=900,
                bbox_inches="tight"
            )
            print(f"Plot saved at {filepath_out}")

            # display the figure
            plt.show()

        except Exception as e:
            print("The error raised is: ", e)
        finally:
            print("All Done!")
            self.exit()

    def exit(self):
        exit(0)

    def dem_file_selector(self):
        fn = filedialog.askopenfilename(title='Select the input file')
        self.dem_file_name.set(fn)

    def output_file_selector(self):
        fn = filedialog.asksaveasfilename(title='Save As')
        self.output_file_name.set(fn)


root = Tk()
app = Window(root)
root.wm_title("Plot Timeseries Data")
root.mainloop()