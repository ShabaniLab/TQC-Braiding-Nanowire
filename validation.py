import exception

# Nanowire Validation Algorithm which returns a score
def validate_nanowire_state(nanowire,type,msg):
    try:
        min_free_branch = 0
        if type==2:
            min_free_branch = 1
        elif type==1:
            min_free_branch = 2

        score = validate_empty_branches(nanowire,min_free_branch,msg)
        return score
    except exception.InvalidNanowireStateException:
        raise

# Checks if there are at least 2 empty branches in every intersection
def validate_empty_branches(nanowire,min_free_branch,msg):
    score = 0
    valid = False

    for intersection in nanowire:
        free_b = 0
        for branch in intersection:
            min_free_pos = len(branch)
            free_p = 0
            for tup in branch:
                if list(tup.values())[0]==0:
                    free_p += 1
                else:
                    free_p = 0
            if free_p>=min_free_pos:
                free_b += 1
        if free_b>=min_free_branch:
            valid = True

    if valid:
        score += 1
    if score==0:
        raise exception.InvalidNanowireStateException(msg)
    return score

# def validate_multi_modal_adjcacency():

# def validate_multi_modal_crossing():
