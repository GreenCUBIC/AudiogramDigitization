from typing import List, Optional
from typing_extensions import TypedDict

class Threshold(TypedDict):
    """Represents a hearing threshold (measurement).
    """
    frequency: int
    threshold: int
    ear: str
    masking: bool
    conduction: str
    measurementType: str

class BoundingBox(TypedDict):
    """Represents the dictionary holding the minimum information
    for a bounding box.
    """
    x: int
    y: int
    width: int
    height: int

class AudiogramDict(TypedDict):
    """Represents the dictionary for an audiogram as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    confidence: Optional[float]

class LabelDict(TypedDict):
    """Represents the dictionary for a label as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    value: str
    confidence: Optional[float]

class SymbolDict(TypedDict):
    """Represents the dictionary for a symbol as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    measurementType: str
    confidence: Optional[float]

class CornerDict(TypedDict):
    """Represents a corner, as annotated.
    """
    frequency: int
    threshold: int
    position: TypedDict("PositionDict", { "horizontal": str, "vertical": str })
    x: float
    y: float

class AudiogramAnnotationDict(TypedDict):
    """Represents an audiogram as structured within an annotation.
    """
    confidence: Optional[float]
    correctionAngle: Optional[float]
    boundingBox: BoundingBox
    corners: List[CornerDict]
    labels: List[LabelDict]
    symbols: List[SymbolDict]
