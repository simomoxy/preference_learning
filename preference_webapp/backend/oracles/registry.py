"""
Oracle Registry for Virtual Decision Makers.

Registers all available oracles for easy access and extensibility.
"""

from backend.core.base_oracle import BaseOracle
from backend.core.registry import Registry


class OracleRegistry(Registry[BaseOracle]):
    """Registry for oracle (virtual decision maker) plugins."""

    def __init__(self):
        super().__init__("Oracle")


# Global registry instance
oracle_registry = OracleRegistry()


# Register built-in oracles
from backend.oracles.biased_oracle import InteractiveBiasedOracle
from backend.oracles.random_oracle import RandomOracle
from backend.oracles.custom_oracle import CustomOracle, CompositeOracle

# Register with names
oracle_registry.register('biased')(InteractiveBiasedOracle)
oracle_registry.register('biased_oracle')(InteractiveBiasedOracle)  # Alias
oracle_registry.register('interactive')(InteractiveBiasedOracle)  # Alias

oracle_registry.register('random')(RandomOracle)
oracle_registry.register('random_baseline')(RandomOracle)  # Alias

oracle_registry.register('custom')(CustomOracle)
oracle_registry.register('composite')(CompositeOracle)


# Convenience functions
def get_oracle(name: str, **kwargs) -> BaseOracle:
    """
    Get an oracle instance by name.

    Args:
        name: Oracle name (e.g., 'biased', 'random', 'custom')
        **kwargs: Arguments to pass to oracle constructor

    Returns:
        Oracle instance

    Raises:
        ValueError: If oracle name not found

    Example:
        >>> oracle = get_oracle('biased', noise=0.2)
        >>> preference = oracle.prefer(mask1, mask2)
    """
    return oracle_registry.get(name, **kwargs)


def list_oracles() -> list:
    """
    List all available oracle names.

    Returns:
        Sorted list of oracle names

    Example:
        >>> print(list_oracles())
        ['biased', 'composite', 'custom', 'random']
    """
    return oracle_registry.list_available()


def register_oracle(name: str):
    """
    Decorator to register a custom oracle.

    Args:
        name: Unique name for the oracle

    Example:
        >>> @register_oracle('my_oracle')
        ... class MyOracle(BaseOracle):
        ...     def prefer(self, mask_a, mask_b):
        ...         return True
    """
    return oracle_registry.register(name)


if __name__ == "__main__":
    # Test oracle registry
    print("Available oracles:", list_oracles())

    # Test getting oracles
    biased = get_oracle('biased', noise=0.3)
    print(f"Biased oracle: {biased}")

    random = get_oracle('random', seed=123)
    print(f"Random oracle: {random}")

    print("\n✓ Oracle registry working!")
