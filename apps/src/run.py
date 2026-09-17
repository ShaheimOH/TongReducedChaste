import shutil
import subprocess
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
from functions import stimulate_tong_cell, change_tong_conductances, revert_changes

# changing conductances example (Oestradiol)

percentage_changes = {
    "gna": 0,
    "gcal": -80,   # Oestradiol: gCaL × 0.2
    "gcat": 0,
    "gkca": -10,   # Oestradiol: gK(Ca) × 0.9
    "gb": 0,
    "gk1": -40,    # Oestradiol: gK1 × 0.6
    "gcl": 0,
    "gns": 0,
}

change_tong_conductances(percentage_changes)

# stimulate single uterine cell 

vm, time = stimulate_tong_cell(start_time = 0, end_time = 4000, sampling_timestep = 1)

revert_changes()

plt.plot(time, vm, color='black', linewidth=1.5)
plt.xlabel("Time (s)")
plt.ylabel("Membrane Voltage (mV)")
plt.savefig("/home/chaste/src/projects/TongReducedChaste/uterine_cell_voltage.png",dpi=500)



