from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetSpec:
    """Specification for a single HDF5 dataset"""
    shape: tuple[int, ...]
    dtype: str = 'float64'

    def as_dict(self) -> dict:
        return {"shape": self.shape, "dtype": self.dtype}

    def __or__(self, other):
        if isinstance(other, dict):
            return self.as_dict() | other
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, dict):
            return other | self.as_dict()
        return NotImplemented


