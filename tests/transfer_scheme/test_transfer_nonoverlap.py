"""
Test the transfer schemes using non-overlapping sub-communicators

"""

import numpy as np
from funtofem import TransferScheme
from mpi4py import MPI
import unittest


class TransferSchemeTest(unittest.TestCase):

    N_PROCS = 5

    def _get_aero_nnodes(self, comm):
        if comm != MPI.COMM_NULL:
            return 55 + 11 * comm.rank
        return 0

    def _get_struct_nnodes(self, comm):
        if comm != MPI.COMM_NULL:
            return 37 + 7 * comm.rank
        return 0

    def _get_comms(self, comm):
        if comm.size != 5:
            raise ValueError("Test can only be run with 5 MPI ranks")

        rank = comm.Get_rank()
        struct_root = 0
        aero_root = 2

        if rank < 2:
            color = 55
        else:
            color = 66
        split_comm = comm.Split(color, rank)

        aero_comm = MPI.COMM_NULL
        struct_comm = MPI.COMM_NULL
        if rank < 2:
            struct_comm = split_comm
        else:
            aero_comm = split_comm

        return comm, struct_comm, struct_root, aero_comm, aero_root

    def test_meld(self):
        comm, struct_comm, struct_root, aero_comm, aero_root = self._get_comms(
            MPI.COMM_WORLD
        )

        # Set typical parameter values
        isymm = 1  # Symmetry axis (0, 1, 2 or -1 for no symmetry)
        nn = 10  # Number of nearest neighbors to consider
        beta = 0.5  # Relative decay factor
        transfer = TransferScheme.pyMELD(
            comm, struct_comm, struct_root, aero_comm, aero_root, isymm, nn, beta
        )

        aero_nnodes = self._get_aero_nnodes(aero_comm)
        aero_X = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)
        transfer.setAeroNodes(aero_X)

        struct_nnodes = self._get_struct_nnodes(struct_comm)
        struct_X = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        transfer.setStructNodes(struct_X)

        transfer.initialize()

        # Set random forces
        uS = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        fA = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)

        dh = 1e-6
        rtol = 1e-5
        atol = 1e-30
        if TransferScheme.dtype == complex:
            dh = 1e-30
            rtol = 1e-9
            atol = 1e-30

        fail = transfer.testAllDerivatives(uS, fA, dh, rtol, atol)

        assert fail == 0

        return

    def test_rbf(self):
        comm, struct_comm, struct_root, aero_comm, aero_root = self._get_comms(
            MPI.COMM_WORLD
        )

        # Set typical parameter values
        rbf_type = TransferScheme.PY_MULTIQUADRIC
        sampling_ratio = 1
        transfer = TransferScheme.pyRBF(
            comm,
            struct_comm,
            struct_root,
            aero_comm,
            aero_root,
            rbf_type,
            sampling_ratio,
        )

        aero_nnodes = self._get_aero_nnodes(aero_comm)
        aero_X = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)
        transfer.setAeroNodes(aero_X)

        struct_nnodes = self._get_struct_nnodes(struct_comm)
        struct_X = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        transfer.setStructNodes(struct_X)

        transfer.initialize()

        # Set random forces
        uS = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        fA = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)

        dh = 1e-6
        rtol = 1e-5
        atol = 1e-30
        if TransferScheme.dtype == complex:
            dh = 1e-30
            rtol = 1e-9
            atol = 1e-30

        fail = transfer.testAllDerivatives(uS, fA, dh, rtol, atol)

        assert fail == 0

        return

    def test_linear_meld(self):
        comm, struct_comm, struct_root, aero_comm, aero_root = self._get_comms(
            MPI.COMM_WORLD
        )

        # Set typical parameter values
        isymm = 1  # Symmetry axis (0, 1, 2 or -1 for no symmetry)
        nn = 10  # Number of nearest neighbors to consider
        beta = 0.5  # Relative decay factor
        transfer = TransferScheme.pyLinearizedMELD(
            comm, struct_comm, struct_root, aero_comm, aero_root, isymm, nn, beta
        )

        aero_nnodes = self._get_aero_nnodes(aero_comm)
        aero_X = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)
        transfer.setAeroNodes(aero_X)

        struct_nnodes = self._get_struct_nnodes(struct_comm)
        struct_X = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        transfer.setStructNodes(struct_X)

        transfer.initialize()

        # Set random forces
        uS = np.random.random(3 * struct_nnodes).astype(TransferScheme.dtype)
        fA = np.random.random(3 * aero_nnodes).astype(TransferScheme.dtype)

        dh = 1e-6
        rtol = 1e-5
        atol = 1e-30
        if TransferScheme.dtype == complex:
            dh = 1e-30
            rtol = 1e-9
            atol = 1e-30

        fail = transfer.testAllDerivatives(uS, fA, dh, rtol, atol)

        assert fail == 0

        return


if __name__ == "__main__":
    test = TransferSchemeTest()
    test.test_meld()
    test.test_rbf()
    test.test_linear_meld()
