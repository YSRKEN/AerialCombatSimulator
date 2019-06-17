import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class Kammusu:
    id: int
    type: int
    name: str
    aa: int
    slot_size: int
    slot: List[int]
    weapon: List[int]
    kammusu_flg: bool
    attack: int
    torpedo: int
    anti_sub: int
