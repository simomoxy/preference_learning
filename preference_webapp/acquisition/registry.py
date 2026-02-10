"""
Acquisition function registry.

Provides a central registry for all available acquisition functions.
"""

from backend.core.registry import AcquisitionRegistry
from acquisition.acquisition import (
    RandomAcquisition,
    ThompsonSamplingAcquisition,
    UCBAcquisition,
    EIAcquisition,
    VarianceAcquisition,
)

# Create global acquisition registry instance
acquisition_registry = AcquisitionRegistry()

# Register built-in acquisition functions
acquisition_registry.register('random')(RandomAcquisition)
acquisition_registry.register('thompson_sampling')(ThompsonSamplingAcquisition)
acquisition_registry.register('ts')(ThompsonSamplingAcquisition)  # Alias
acquisition_registry.register('ucb')(UCBAcquisition)
acquisition_registry.register('ei')(EIAcquisition)
acquisition_registry.register('variance')(VarianceAcquisition)


def get_acquisition(name: str, **kwargs):
    """
    Get an acquisition function instance by name.

    Args:
        name: Name of the acquisition function
        **kwargs: Arguments to pass to acquisition function constructor

    Returns:
        Acquisition function instance

    Raises:
        ValueError: If acquisition function name not found

    Example:
        >>> acq_fn = get_acquisition('thompson_sampling')
        >>> pairs = acq_fn.acquire(model, likelihood, candidates, features, n_pairs=10)
    """
    return acquisition_registry.get(name, **kwargs)


def list_acquisitions():
    """
    List all available acquisition functions.

    Returns:
        Sorted list of acquisition function names

    Example:
        >>> print(list_acquisitions())
        ['ei', 'random', 'thompson_sampling', 'ts', 'ucb', 'variance']
    """
    return acquisition_registry.list_available()


# Export key items
__all__ = [
    'acquisition_registry',
    'get_acquisition',
    'list_acquisitions',
    'RandomAcquisition',
    'ThompsonSamplingAcquisition',
    'UCBAcquisition',
    'EIAcquisition',
    'VarianceAcquisition',
]
