import numpy as np
from fairness.node_service.rui import RUI

__author__ = 'Patrick'


class VM:

    def __init__(self, vm_id, vrs, owner):
        """
        :param vrs: sequence (list, np.array, etc.) that specifies the VM's VRs
        :param owner: string that specifies the VM's owner (must be key in the owner dictionary)
        :param node: this is the node object created in a prior step
        """
        # assert len(vrs) == len(VM.nri)
        # assert owner in node.owners

        self.vm_id = vm_id
        self.vrs = np.array(vrs)
        self.owner = owner
        self.rui = None             # change to RUI()
        self.endowment = None

    def update_rui(self, rui):
        """
        :param rui: the VM's RUI in the current measurement period
        """
        # assert len(rui) == len(VM.global_normalization)
        self.rui = np.array(rui)
