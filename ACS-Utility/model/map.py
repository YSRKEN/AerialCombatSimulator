import dataclasses


@dataclasses.dataclass(frozen=True)
class Map:
    id: int
    name: str
    info_url: str
    image_url: str
