import os, unittest, numpy as np
from mpi4py import MPI
from tacs import TACS
from funtofem import TransferScheme
from funtofem.model import FUNtoFEMmodel, Variable, Scenario, Body, Function
from funtofem.interface import (
    TestAerodynamicSolver,
    TacsSteadyInterface,
    SolverManager,
    TestResult,
)
from funtofem.driver import (
    FUNtoFEMnlbgs,
    TransferSettings,
    TacsOnewayDriver,
    TestAeroOnewayDriver,
)

from bdf_test_utils import thermoelasticity_callback, elasticity_callback

np.random.seed(1234567)

comm = MPI.COMM_WORLD
base_dir = os.path.dirname(os.path.abspath(__file__))
bdf_filename = os.path.join(base_dir, "input_files", "test_bdf_file.bdf")

results_folder = os.path.join(base_dir, "results")
if comm.rank == 0:  # make the results folder if doesn't exist
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)

complex_mode = TransferScheme.dtype == complex and TACS.dtype == complex


class TestTacsOnewayDriver(unittest.TestCase):
    """
    This class performs unit test on the oneway-coupled TacsSteadyAnalysisDriver
    which uses fixed aero loads
    TODO : in the case of an unsteady one, add methods for those too?
    """

    FILENAME = "oneway-driver.txt"
    FILEPATH = os.path.join(results_folder, FILENAME)

    def test_aeroelastic(self):
        # build the model and driver
        model = FUNtoFEMmodel("wedge")
        plate = Body.aeroelastic("plate", boundary=1)
        Variable.structural("thickness").set_bounds(
            lower=0.01, value=0.1, upper=1.0
        ).register_to(plate)
        plate.register_to(model)

        # build the scenario
        scenario = Scenario.steady("test", steps=200).include(Function.ksfailure())
        scenario.register_to(model)

        # build the tacs interface, coupled driver, and oneway driver
        comm = MPI.COMM_WORLD
        solvers = SolverManager(comm)
        solvers.flow = TestAerodynamicSolver(comm, model)
        solvers.structural = TacsSteadyInterface.create_from_bdf(
            model, comm, 1, bdf_filename, callback=elasticity_callback
        )
        transfer_settings = TransferSettings(npts=5)
        coupled_driver = FUNtoFEMnlbgs(
            solvers, transfer_settings=transfer_settings, model=model
        )
        oneway_driver = TacsOnewayDriver.prime_loads(coupled_driver, transfer_settings)

        # run teh oomplex step test
        max_rel_error = TestResult.derivative_test(
            "oneway-aeroelastic",
            model,
            oneway_driver,
            TestTacsOnewayDriver.FILEPATH,
            complex_mode=complex_mode,
        )
        rtol = 1e-7 if complex_mode else 1e-3
        self.assertTrue(max_rel_error < rtol)

        return

    def test_aerothermal(self):
        # build the model and driver
        model = FUNtoFEMmodel("wedge")
        plate = Body.aerothermal("plate", boundary=1)
        Variable.structural("thickness").set_bounds(
            lower=0.01, value=0.1, upper=2.0
        ).register_to(plate)
        plate.register_to(model)

        # build the scenario
        scenario = (
            Scenario.steady("test", steps=150)
            .include(Function.ksfailure())
            .include(Function.temperature())
        )
        scenario.register_to(model)

        # build the tacs interface, coupled driver, and oneway driver
        comm = MPI.COMM_WORLD
        solvers = SolverManager(comm)
        solvers.flow = TestAerodynamicSolver(comm, model)
        solvers.structural = TacsSteadyInterface.create_from_bdf(
            model, comm, 1, bdf_filename, callback=thermoelasticity_callback
        )
        transfer_settings = TransferSettings(npts=5)
        coupled_driver = FUNtoFEMnlbgs(
            solvers, transfer_settings=transfer_settings, model=model
        )
        oneway_driver = TacsOnewayDriver.prime_loads(coupled_driver, transfer_settings)

        # run teh oomplex step test
        max_rel_error = TestResult.derivative_test(
            "oneway-aerothermal",
            model,
            oneway_driver,
            TestTacsOnewayDriver.FILEPATH,
            complex_mode=complex_mode,
        )
        rtol = 1e-7 if complex_mode else 1e-3
        self.assertTrue(max_rel_error < rtol)

        return

    def test_aerothermoelastic(self):
        # build the model and driver
        model = FUNtoFEMmodel("wedge")
        plate = Body.aerothermoelastic("plate", boundary=1)
        Variable.structural("thickness").set_bounds(
            lower=0.01, value=0.1, upper=1.0
        ).register_to(plate)
        plate.register_to(model)

        # build the scenario
        scenario = (
            Scenario.steady("test", steps=150)
            .include(Function.ksfailure())
            .include(Function.temperature())
        )
        scenario.register_to(model)

        # build the tacs interface, coupled driver, and oneway driver
        comm = MPI.COMM_WORLD
        solvers = SolverManager(comm)
        solvers.flow = TestAerodynamicSolver(comm, model)
        solvers.structural = TacsSteadyInterface.create_from_bdf(
            model, comm, 1, bdf_filename, callback=thermoelasticity_callback
        )
        transfer_settings = TransferSettings(npts=5)
        coupled_driver = FUNtoFEMnlbgs(
            solvers, transfer_settings=transfer_settings, model=model
        )
        oneway_driver = TacsOnewayDriver.prime_loads(coupled_driver, transfer_settings)

        # run teh oomplex step test
        max_rel_error = TestResult.derivative_test(
            "oneway-aerothermoelastic",
            model,
            oneway_driver,
            TestTacsOnewayDriver.FILEPATH,
            complex_mode=complex_mode,
        )
        rtol = 1e-7 if complex_mode else 1e-3
        self.assertTrue(max_rel_error < rtol)
        return

    def test_aeroelastic_aero_oneway(self):
        """test using a oneway aero driver"""
        # build the model and driver
        model = FUNtoFEMmodel("wedge")
        plate = Body.aeroelastic("plate", boundary=1)
        Variable.structural("thickness").set_bounds(
            lower=0.01, value=0.1, upper=1.0
        ).register_to(plate)
        plate.register_to(model)

        # build the scenario
        scenario = Scenario.steady("test", steps=200).include(Function.ksfailure())
        scenario.register_to(model)

        # build the tacs interface, coupled driver, and oneway driver
        comm = MPI.COMM_WORLD
        solvers = SolverManager(comm)
        solvers.flow = TestAerodynamicSolver(comm, model)
        solvers.structural = TacsSteadyInterface.create_from_bdf(
            model, comm, 1, bdf_filename, callback=elasticity_callback
        )
        transfer_settings = TransferSettings(npts=5)
        aero_driver = TestAeroOnewayDriver(solvers, model, transfer_settings)
        oneway_driver = TacsOnewayDriver.prime_loads(aero_driver, transfer_settings)

        # run teh oomplex step test
        max_rel_error = TestResult.derivative_test(
            "oneway-aeroelastic-testaero_driver",
            model,
            oneway_driver,
            TestTacsOnewayDriver.FILEPATH,
            complex_mode=complex_mode,
        )
        rtol = 1e-7 if complex_mode else 1e-3
        self.assertTrue(max_rel_error < rtol)

        return


if __name__ == "__main__":
    open(TestTacsOnewayDriver.FILEPATH, "w").close()
    unittest.main()
