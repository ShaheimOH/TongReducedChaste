#include "AbstractCvodeCell.hpp"
#include "CellMLToSharedLibraryConverter.hpp"
#include "EulerIvpOdeSolver.hpp"
#include "ExecutableSupport.hpp"
#include "FileFinder.hpp"
#include "OdeSolution.hpp"
#include "OutputFileHandler.hpp"
#include "SimpleStimulus.hpp"

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char* argv[])
{
    ExecutableSupport::StandardStartup(&argc, &argv);

    // Command-line arguments:
    // ./TestTongCellML <start_time_ms> <end_time_ms> <sampling_timestep_ms>
    if (argc != 4)
    {
        std::cerr << "Usage: " << argv[0] << " <start_time_ms> <end_time_ms> <sampling_timestep_ms>\n";
        ExecutableSupport::FinalizePetsc();
        return 1;
    }

    const double start_time = std::stod(argv[1]);
    const double end_time = std::stod(argv[2]);
    const double sampling_timestep = std::stod(argv[3]);

    // Stimulus
    const double stimulus_magnitude = -0.5;   // pA/pF
    const double stimulus_duration = 2000.0;  // ms
    const double stimulus_start = 1000.0;     // ms

    boost::shared_ptr<SimpleStimulus> p_stimulus(
        new SimpleStimulus(stimulus_magnitude, stimulus_duration, stimulus_start)
    );

    boost::shared_ptr<EulerIvpOdeSolver> p_solver(new EulerIvpOdeSolver);

    // CellML model
    FileFinder cellml_file("projects/TongReducedChaste/cellml/Tong_Reduced.cellml", RelativeTo::ChasteSourceRoot);
    OutputFileHandler output_handler("converted_file_folder", true);
    FileFinder copied_cellml_file = output_handler.CopyFileTo(cellml_file);

    // Convert CellML
    CellMLToSharedLibraryConverter converter(true);
    converter.SetOptions({"--cvode", "--use-analytic-jacobian"});
    DynamicCellModelLoaderPtr p_loader = converter.Convert(copied_cellml_file);

    AbstractCvodeCell* p_tong_cell = dynamic_cast<AbstractCvodeCell*>(
        p_loader->CreateCell(p_solver, p_stimulus)
    );

    // Simulate cell
    p_tong_cell->SetMaxTimestep(0.1);
    OdeSolution solution = p_tong_cell->Compute(start_time, end_time, sampling_timestep);

    // Extract membrane voltage
    unsigned voltage_index = p_tong_cell->GetSystemInformation()->GetStateVariableIndex("membrane_voltage");
    std::vector<double> voltages = solution.GetVariableAtIndex(voltage_index);
    const std::vector<double>& times = solution.rGetTimes();

    // Save time and Vm
    std::ofstream vm_file("/home/chaste/src/projects/TongReducedChaste/vm.txt");
    for (unsigned i = 0; i < times.size(); ++i)
    {
        vm_file << times[i] << "\t" << voltages[i] << "\n";
    }
    vm_file.close();

    ExecutableSupport::FinalizePetsc();

    return 0;
}