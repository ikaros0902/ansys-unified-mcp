"""Prepare the official mixing elbow mesh, or solve an explicitly configured case."""
import argparse
from pathlib import Path


def prepare_mesh(meshing, geometry_file, version):
    """Use the official workflow for Fluent 251/252 (legacy) or 261 (new)."""
    if version == 261:
        workflow = meshing.watertight(legacy=False)
        task = workflow.import_geometry
        task.file_name = str(geometry_file)
        task.length_unit = "in"
        task()
        workflow.add_local_sizing_wtm.add_child_to_task()
        workflow.add_local_sizing_wtm()
        workflow.create_surface_mesh.cfd_surface_mesh_controls.max_size = 0.3
        workflow.create_surface_mesh()
        task = workflow.describe_geometry
        task.update_child_tasks(setup_type_changed=False)
        task.setup_type = "fluid"
        task.update_child_tasks(setup_type_changed=True)
        task()
        task = workflow.update_boundaries
        task.boundary_zone_list = ["wall-inlet"]
        task.boundary_label_list = ["wall-inlet"]
        task.boundary_label_type_list = ["wall"]
        task.old_boundary_label_list = ["wall-inlet"]
        task.old_boundary_label_type_list = ["velocity-inlet"]
        task()
        workflow.update_regions()
        task = workflow.add_boundary_layers
        task.control_name = "smooth-transition_1"
        task.insert_compound_child_task()
        workflow.add_boundary_layers_child_1()
        task = workflow.create_volume_mesh_wtm
        task.volume_fill = "poly-hexcore"
        task.volume_fill_controls.hex_max_cell_length = 0.3
        task()
    else:
        workflow = meshing.workflow
        workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
        tasks = workflow.TaskObject
        tasks["Import Geometry"].Arguments.set_state(
            {"FileName": str(geometry_file), "LengthUnit": "in"})
        tasks["Import Geometry"].Execute()
        tasks["Add Local Sizing"].Execute()
        tasks["Generate the Surface Mesh"].Arguments.set_state(
            {"CFDSurfaceMeshControls": {"MaxSize": 0.3}})
        tasks["Generate the Surface Mesh"].Execute()
        task = tasks["Describe Geometry"]
        task.UpdateChildTasks(SetupTypeChanged=False)
        task.Arguments.set_state(
            {"SetupType": "The geometry consists of only fluid regions with no voids"})
        task.UpdateChildTasks(SetupTypeChanged=True)
        task.Execute()
        tasks["Update Boundaries"].Arguments.set_state({
            "BoundaryLabelList": ["wall-inlet"], "BoundaryLabelTypeList": ["wall"],
            "OldBoundaryLabelList": ["wall-inlet"],
            "OldBoundaryLabelTypeList": ["velocity-inlet"]})
        tasks["Update Boundaries"].Execute()
        tasks["Update Regions"].Execute()
        task = tasks["Add Boundary Layers"]
        task.Arguments.set_state({"BLControlName": "smooth-transition_1"})
        task.AddChildToTask()
        task.InsertCompoundChildTask()
        tasks["smooth-transition_1"].Execute()
        task = tasks["Generate the Volume Mesh"]
        task.Arguments.set_state({
            "VolumeFill": "poly-hexcore",
            "VolumeFillControls": {"HexMaxCellLength": 0.3}})
        task.Execute()


def run_mixing_elbow_simulation(
    output_dir="./results_mixing_elbow", processor_count=4, iter_count=150,
    show_gui=False, *, phase="prepare", product_version=261,
    allow_launch=False, allow_model_changes=False, allow_solve=False,
    geometry_file=None, case_file=None,
):
    """Require separate authorization before launch, model changes, and solve."""
    if phase not in ("prepare", "solve") or product_version not in (251, 252, 261):
        raise ValueError("Expected prepare/solve and product version 251, 252, or 261")
    if processor_count < 1 or iter_count < 1:
        raise ValueError("Processor and iteration counts must be positive")
    if not allow_launch or not allow_model_changes:
        raise PermissionError("Launch and model changes require separate authorization")
    if phase == "solve" and not allow_solve:
        raise PermissionError("Solving requires explicit authorization")
    input_file = geometry_file if phase == "prepare" else case_file
    if phase == "solve" and not input_file:
        raise ValueError("Solve requires an explicitly configured case file")
    if input_file and not Path(input_file).is_file():
        raise FileNotFoundError(input_file)
    output = Path(output_dir).resolve()
    target = output / ("mixing_elbow.msh.h5" if phase == "prepare"
                       else "mixing_elbow_solution.cas.h5")
    if target.exists() or target.with_name("mixing_elbow_solution.dat.h5").exists():
        raise FileExistsError("Choose a fresh output directory; existing results are preserved")

    import ansys.fluent.core as pyfluent
    from ansys.fluent.core import examples

    if phase == "prepare" and input_file is None:
        input_file = examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")
    output.mkdir(parents=True, exist_ok=True)
    session = pyfluent.launch_fluent(
        product_version=product_version, mode="meshing" if phase == "prepare" else "solver",
        precision="double", processor_count=processor_count,
        ui_mode="gui" if show_gui else "no_gui", cwd=str(output))
    try:
        if phase == "prepare":
            prepare_mesh(session, input_file, product_version)
            session.tui.file.write_mesh(str(target))
        else:
            session.settings.file.read(file_type="case", file_name=str(Path(input_file).resolve()))
            session.settings.solution.initialization.hybrid_initialize()
            session.settings.solution.run_calculation.iterate(iter_count=iter_count)
            session.settings.file.write(file_type="case-data", file_name=str(target))
        required = [target]
        if phase == "solve":
            required.append(target.with_name("mixing_elbow_solution.dat.h5"))
        if any(not path.is_file() or not path.stat().st_size for path in required):
            raise RuntimeError("Expected nonempty output files were not produced")
        return [str(path) for path in required]
    finally:
        session.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "solve"), default="prepare")
    parser.add_argument("--version", type=int, choices=(251, 252, 261), default=261)
    parser.add_argument("--output-dir", default="./results_mixing_elbow")
    parser.add_argument("--cores", type=int, default=4)
    parser.add_argument("--iters", type=int, default=150)
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--geometry-file")
    parser.add_argument("--case-file")
    parser.add_argument("--allow-launch", action="store_true")
    parser.add_argument("--allow-model-changes", action="store_true")
    parser.add_argument("--allow-solve", action="store_true")
    args = parser.parse_args()
    print(run_mixing_elbow_simulation(
        args.output_dir, args.cores, args.iters, args.gui, phase=args.phase,
        product_version=args.version, allow_launch=args.allow_launch,
        allow_model_changes=args.allow_model_changes, allow_solve=args.allow_solve,
        geometry_file=args.geometry_file, case_file=args.case_file))
