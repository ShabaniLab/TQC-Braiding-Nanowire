"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Exception

Class:
    1. NoEmptyPositionException
    2. InvalidNanowireStateException
        1. NoEmptyBranchException
        2. MultiModalCrossingException
    3. InvalidMovementException
        1. PathBlockedException

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

class InvalidMovementException(Exception):
    """
    When the Preprocess movement isn't possible
    """

class PathBlockedException(InvalidMovementException):
    """
    When the path is blocked by another particle
    """
