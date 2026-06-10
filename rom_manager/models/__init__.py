"""Model (schema) layer for ROM Manager.

Re-exports the Pydantic request/response models so the historical
``from rom_manager.models import ...`` import path keeps working now that the
schemas live in :mod:`rom_manager.models.schemas`.
"""

from rom_manager.models.schemas import (
    ConvertRequest,
    ConvertResult,
    GameCodeLookup,
    GenerateCueRequest,
    GenerateCueResult,
    RenameResult,
)

__all__ = [
    "ConvertRequest",
    "ConvertResult",
    "GameCodeLookup",
    "GenerateCueRequest",
    "GenerateCueResult",
    "RenameResult",
]
