# TongReducedChaste

<img width="896" height="346" alt="image" src="https://github.com/user-attachments/assets/45825b03-10ff-480d-a69b-d2266219ec77" />

Chaste-based simulation of the reduced Tong uterine smooth muscle cell model, with Python utilities for modifying ion-channel conductances and plotting membrane voltage. Image shown is a replication of this study via the reduced model: https://www.physoc.org/abstracts/mathematical-modelling-of-electrical-action-potentials-in-a-uterine-smooth-muscle-cell/

Link to reduced model paper: https://doi.org/10.1371/journal.pcbi.1011359

Link to original model paper: https://doi.org/10.1371/journal.pone.0018685

Link to Chaste software paper: https://joss.theoj.org/papers/10.21105/joss.01848

This was a project completed during the Chaste Oxford Hackathon 2026. 

** Note ** We used Chaste via Docker (implementation details here: https://github.com/Chaste/chaste-docker).

## Features

- Run the Tong CellML model through Chaste (one action potential simulation)
- Change selected conductances by percentage
- Restore the original CellML model after simulation
- Load and plot membrane-voltage traces

## Structure

```text
TongReducedChaste/
├── apps/src/TongCellML.cpp
├── cellml/
│   ├── Tong_Reduced.cellml
│   └── Tong_Reduced_original.cellml
├── functions.py
└── README.md
```

## Build

Inside the Chaste Docker container:

```bash
cd /home/chaste/build
cmake /home/chaste/src
make -j4 TongCellML
```

Executable:

```text
/home/chaste/build/projects/TongReducedChaste/apps/TongCellML
```

## Python environment

```bash
cd /home/chaste/src/projects/TongReducedChaste
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy matplotlib
```

## Run a simulation

```python
from functions import stimulate_tong_cell

vm, time = stimulate_tong_cell(
    start_time=0,
    end_time=4000,
    sampling_timestep=1,
)
```

## Change conductances

```python
from functions import change_tong_conductances

percentage_changes = {
    "gna": -10,
    "gcal": -50,
    "gcat": 0,
    "gkca": 20,
    "gb": 0,
    "gk1": -15,
    "gcl": 0,
    "gns": 10,
}

change_tong_conductances(percentage_changes)
```

`-50` means a 50% reduction, while `20` means a 20% increase.

## Restore the original model

```python
from functions import revert_changes

revert_changes()
```

This restores `Tong_Reduced.cellml` from `Tong_Reduced_original.cellml`.

## Recommended workflow

```python
from functions import (
    stimulate_tong_cell,
    change_tong_conductances,
    revert_changes,
)

percentage_changes = {
    "gcal": -50,
    "gkca": 20,
}

try:
    change_tong_conductances(percentage_changes)
    vm, time = stimulate_tong_cell(0, 4000, 1)
finally:
    revert_changes()
```

## Notes

- Keep `Tong_Reduced_original.cellml` unchanged.
- `Tong_Reduced.cellml` is the working model used by Chaste.
- Conductance editing currently depends on fixed line locations in the CellML file.
