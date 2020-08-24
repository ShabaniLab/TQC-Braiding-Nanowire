## Custom Exceptions
# When there are no available empty positions on the branches to perform the braiding
class NoEmptyPositionException(Exception):
    pass

# When the resulting Nanowire state is Invalid => Braiding stops
class InvalidNanowireStateException(Exception):
    pass

# When the path is blocked by another particle
class PathBlockedException(Exception):
    pass
