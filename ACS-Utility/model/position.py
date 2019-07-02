import dataclasses


@dataclasses.dataclass(frozen=True)
class Position:
    id: int
    map: int
    name: str
    final_flg: bool
    formation: int
