"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Exception

Class:
    1. NoEmptyPositionException
    2. InvalidNanowireStateException
    3. NoEmptyBranchException
    4. MultiModalCrossingException
    5. PathBlockedException

"""

class NoEmptyPositionException(Exception):
    """
    When there are no available empty positions on the branches to perform the braiding
    """

class InvalidNanowireStateException(Exception):
    """
    When the resulting Nanowire state is Invalid => Braiding stops
    """

class NoEmptyBranchException(InvalidNanowireStateException):
    """
    When there are less than 2 empty branches in an intersection
    """

class MultiModalCrossingException(InvalidNanowireStateException):
    """
    When Rule 3 is violated
    """

class PathBlockedException(Exception):
    """
    When the path is blocked by another particle
    """
