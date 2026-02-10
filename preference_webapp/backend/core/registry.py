"""
Plugin Registry System for Preference Learning Webapp.

Provides a flexible, extensible registration system for:
- Acquisition functions
- Learning strategies
- Oracles (virtual decision makers)
- Encoders

Usage:
    @AcquisitionRegistry.register('my_acquisition')
    class MyAcquisition(AcquisitionFunction):
        pass

    # Later:
    acq = AcquisitionRegistry.get('my_acquisition', param1=value1)
"""

from typing import Dict, Type, List, Any
from typing import TypeVar, Generic


T = TypeVar('T')


class Registry(Generic[T]):
    """Generic registry for plugin components."""

    def __init__(self, name: str):
        """
        Initialize registry.

        Args:
            name: Name of the registry (e.g., 'Acquisition')
        """
        self._registry: Dict[str, Type[T]] = {}
        self._name = name

    def register(self, name: str):
        """
        Decorator to register a component.

        Args:
            name: Unique name for the component

        Returns:
            Decorator function

        Example:
            @registry.register('my_component')
            class MyComponent(BaseClass):
                pass
        """
        def decorator(component_class: Type[T]) -> Type[T]:
            if name in self._registry:
                raise ValueError(f"{self._name} '{name}' already registered. "
                               f"Use a different name or unregister first.")
            self._registry[name] = component_class
            return component_class
        return decorator

    def get(self, name: str, **kwargs) -> T:
        """
        Get a component instance by name.

        Args:
            name: Name of the component
            **kwargs: Arguments to pass to component constructor

        Returns:
            Component instance

        Raises:
            ValueError: If component name not found
        """
        if name not in self._registry:
            available = list(self._registry.keys())
            raise ValueError(f"Unknown {self._name.lower()}: '{name}'. "
                           f"Available: {available}")
        component_class = self._registry[name]
        return component_class(**kwargs)

    def list_available(self) -> List[str]:
        """
        List all registered component names.

        Returns:
            Sorted list of component names
        """
        return sorted(self._registry.keys())

    def is_registered(self, name: str) -> bool:
        """
        Check if a component is registered.

        Args:
            name: Component name

        Returns:
            True if registered, False otherwise
        """
        return name in self._registry

    def unregister(self, name: str) -> None:
        """
        Unregister a component.

        Args:
            name: Component name

        Raises:
            ValueError: If component not found
        """
        if name not in self._registry:
            raise ValueError(f"{self._name} '{name}' not registered")
        del self._registry[name]

    def clear(self) -> None:
        """Clear all registered components."""
        self._registry.clear()


# Global registries for each component type

# Import base classes here to avoid circular imports
# These will be defined in separate files (base_acquisition.py, base_strategy.py, etc.)
# We'll set up the registries in those files instead

from backend.core.base_acquisition import AcquisitionFunction
from backend.core.base_strategy import LearningStrategy
from backend.core.base_oracle import BaseOracle
from backend.core.base_encoder import BaseEncoder


class AcquisitionRegistry(Registry[AcquisitionFunction]):
    """Registry for acquisition functions."""

    def __init__(self):
        super().__init__("Acquisition")


class StrategyRegistry(Registry[LearningStrategy]):
    """Registry for learning strategies."""

    def __init__(self):
        super().__init__("Strategy")


class OracleRegistry(Registry[BaseOracle]):
    """Registry for oracles (virtual decision makers)."""

    def __init__(self):
        super().__init__("Oracle")


class EncoderRegistry(Registry[BaseEncoder]):
    """Registry for feature encoders."""

    def __init__(self):
        super().__init__("Encoder")


# Global instances
acquisition_registry = AcquisitionRegistry()
strategy_registry = StrategyRegistry()
oracle_registry = OracleRegistry()
encoder_registry = EncoderRegistry()


# Helper functions for backward compatibility
def register_acquisition(name: str):
    """Decorator to register an acquisition function."""
    return acquisition_registry.register(name)


def register_strategy(name: str):
    """Decorator to register a learning strategy."""
    return strategy_registry.register(name)


def register_oracle(name: str):
    """Decorator to register an oracle."""
    return oracle_registry.register(name)


def register_encoder(name: str):
    """Decorator to register an encoder."""
    return encoder_registry.register(name)
