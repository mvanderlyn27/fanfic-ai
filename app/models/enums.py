from enum import Enum

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-Binary"
    OTHER = "Other"

class POVType(str, Enum):
    FIRST_PERSON = "1st person"
    THIRD_PERSON_LIMITED = "3rd person limited"
    THIRD_PERSON_OMNISCIENT = "3rd person omniscient"

class RelationshipStructure(str, Enum):
    MONOGAMOUS = "Monogamous"
    POLYAMOROUS = "Polyamorous"
    OPEN = "Open Relationship"

class Ending(str, Enum):
    HEA = "HEA"
    HFN = "HFN"