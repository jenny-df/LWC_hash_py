

def cf(left, right, msg):
    tmp = right << 5 + msg # TODO: figure out a const other than 5
    new_left = ^ left
    new_right = ^ left ^ 1
    return new_left, new_right

