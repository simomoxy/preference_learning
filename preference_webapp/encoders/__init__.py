"""
Feature encoders for segmentation masks.
"""

from encoders.handcrafted_encoder import HandcraftedEncoder
from encoders.registry import encoder_registry, get_encoder, list_encoders

__all__ = [
    'HandcraftedEncoder',
    'encoder_registry',
    'get_encoder',
    'list_encoders',
]
