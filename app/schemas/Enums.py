from enum import Enum


class GenderEnum(str, Enum):
    """
    Enum for gender. Used to limit the possible values
    """

    male = "Male"
    female = "Female"
    other = "Other"
