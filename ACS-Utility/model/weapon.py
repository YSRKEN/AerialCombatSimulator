import dataclasses


@dataclasses.dataclass(frozen=True)
class Weapon:
    id: int
    type: int
    name: str
    aa: int
    accuracy: int
    interception: int
    radius: int
    for_kammusu_flg: bool
    attack: int
    torpedo: int
    anti_sub: int
    bomber: int