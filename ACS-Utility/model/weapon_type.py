import dataclasses


@dataclasses.dataclass(frozen=True)
class WeaponType:
    id: int
    name: str
    short_name: str
    wikia_name: str
