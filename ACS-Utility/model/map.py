import dataclasses


@dataclasses.dataclass(frozen=True)
class Map:
    name: str
    info_url: str
    image_url: str
