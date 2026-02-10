"""
Encoder registry for feature encoders.

Provides a central registry for all available encoders.
"""

from backend.core.registry import EncoderRegistry
from encoders.handcrafted_encoder import HandcraftedEncoder

# Create global encoder registry instance
encoder_registry = EncoderRegistry()

# Register built-in encoders
encoder_registry.register('handcrafted')(HandcraftedEncoder)
encoder_registry.register('handcrafted_features')(HandcraftedEncoder)  # Alias


def get_encoder(name: str, **kwargs):
    """
    Get an encoder instance by name.

    Args:
        name: Name of the encoder
        **kwargs: Arguments to pass to encoder constructor

    Returns:
        Encoder instance

    Raises:
        ValueError: If encoder name not found

    Example:
        >>> encoder = get_encoder('handcrafted')
        >>> features = encoder.encode(mask)
    """
    return encoder_registry.get(name, **kwargs)


def list_encoders():
    """
    List all available encoders.

    Returns:
        Sorted list of encoder names

    Example:
        >>> print(list_encoders())
        ['handcrafted', 'handcrafted_features']
    """
    return encoder_registry.list_available()


# Export key items
__all__ = [
    'encoder_registry',
    'get_encoder',
    'list_encoders',
    'HandcraftedEncoder',
]
