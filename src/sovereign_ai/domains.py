"""The five deployment domains defined by the blueprint (Table 1)."""
from enum import Enum


class DeploymentDomain(str, Enum):
    AWS_COMMERCIAL = "aws-commercial"
    AWS_EUSC = "aws-eusc"
    VMWARE_PRIVATE = "vmware-private"
    HPE_SOVEREIGN = "hpe-sovereign"
    HPE_DISCONNECTED = "hpe-disconnected"

    @property
    def partition(self) -> str:
        if self is DeploymentDomain.AWS_COMMERCIAL:
            return "aws"
        if self is DeploymentDomain.AWS_EUSC:
            return "aws-eusc"
        return "private"

    @property
    def is_disconnected(self) -> bool:
        return self is DeploymentDomain.HPE_DISCONNECTED
