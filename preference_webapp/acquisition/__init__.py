"""
Acquisition functions for active learning.
"""

from acquisition.acquisition import (
    RandomAcquisition,
    ThompsonSamplingAcquisition,
    UCBAcquisition,
    EIAcquisition,
    VarianceAcquisition,
)
from acquisition.registry import acquisition_registry, get_acquisition, list_acquisitions

__all__ = [
    'RandomAcquisition',
    'ThompsonSamplingAcquisition',
    'UCBAcquisition',
    'EIAcquisition',
    'VarianceAcquisition',
    'acquisition_registry',
    'get_acquisition',
    'list_acquisitions',
]
