import dataclasses


@dataclasses.dataclass(frozen=True)
class PositionFleet:
    position: int
    fleet_index: int
    unit_index: int
    enemy: int
