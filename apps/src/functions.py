import shutil
import subprocess
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# single cell stimulation (one action potential) 

def stimulate_tong_cell(start_time = 0, end_time = 5000, sampling_timestep = 1):

    # run chaste simulation using the compiled C++ executable
    subprocess.run(["/home/chaste/build/projects/TongReducedChaste/apps/TongCellML", str(start_time), str(end_time), str(sampling_timestep)])

    # load the voltage data from the file
    data = np.loadtxt("/home/chaste/src/projects/TongReducedChaste/vm.txt", delimiter="\t")

    time  = data[:,0] / 1000.0  # convert to seconds
    vm   = data[:,1]

    # delete the file after loading the data
    os.remove("/home/chaste/src/projects/TongReducedChaste/vm.txt")

    return vm, time


# change conductances in the Tong model by percentage

def change_tong_conductances(percentage_changes, cell_model_file_path="/home/chaste/src/projects/TongReducedChaste/cellml/Tong_Reduced.cellml", output_file_path=None,):
    """
    Change Tong model conductances by percentage.

    percentage_changes example:
    {
        "gna": -10,
        "gcal": -50,
        "gcat": 0,
        "gkca": 20,
        "gb": 0,
        "gk1": -15,
        "gcl": 0,
        "gns": 10,
    }
    """
    CONDUCTANCE_LINES = {
    "gna": 511,
    "gcal": 519,
    "gcat": 536,
    "gkca": 546,
    "gb": 551,
    "gk1": 568,
    "gcl": 588,
    "gns": 595,
}
    input_path = Path(cell_model_file_path)

    if output_file_path is None:
        output_path = input_path.with_name("Tong_Reduced.cellml")
    else:
        output_path = Path(output_file_path)

    lines = input_path.read_text().splitlines(keepends=True)

    for conductance, percentage_change in percentage_changes.items():
        if conductance not in CONDUCTANCE_LINES:
            raise ValueError(
                f"Unknown conductance '{conductance}'. Available: {list(CONDUCTANCE_LINES)}"
            )

        line_number = CONDUCTANCE_LINES[conductance]
        index = line_number - 1

        # Safety check
        if f"<ci>{conductance}</ci>" not in lines[index - 1]:
            raise RuntimeError(
                f"Expected {conductance} near line {line_number}, but the CellML structure has changed."
            )

        value_line = lines[index]
        match = re.search(r'(<cn[^>]*>)([-+0-9.eE]+)(</cn>)', value_line)

        if match is None:
            raise RuntimeError(f"Could not find value for {conductance}.")

        old_value = float(match.group(2))
        new_value = old_value * (1.0 + percentage_change / 100.0)

        lines[index] = value_line[:match.start(2)] + f"{new_value:.10g}" + value_line[match.end(2):]

        print(f"{conductance}: {old_value:g} -> {new_value:g} ({percentage_change:+g}%)")

    output_path.write_text("".join(lines))
    print(f"\nSaved modified CellML to:\n{output_path}")


# restore .cellml file to original state after changes have been made

def revert_changes():

    original_file = ("/home/chaste/src/projects/TongReducedChaste/""cellml/Tong_Reduced_original.cellml")

    changed_file = ("/home/chaste/src/projects/TongReducedChaste/""cellml/Tong_Reduced.cellml")

    shutil.copyfile(original_file, changed_file)

    print("Tong_Reduced.cellml reverted to original.")