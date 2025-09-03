from enum import Enum, unique

from pydantic import BaseModel


class SingleAllele(BaseModel):
    accession: str
    name: str


class MetaData(BaseModel):
    total: int


class Sequence(BaseModel):
    allele_name: str
    sequence: str


class AllelesNames(BaseModel):
    data: list[SingleAllele]
    meta: MetaData


class AllelesSequences(BaseModel):
    sequences: list[Sequence]


@unique
class SequenceTypes(Enum):
    PROTEIN = "protein"
    GENOMIC = "genomic"
    CODING = "coding"
