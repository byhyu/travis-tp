import numpy as np

def calc_APFD(ranks, failed_ids):
    sum = 0
    for f in failed_ids:
        ind = np.where(ranks == f)
        assert(np.size(ind) == 1)
        sum += (ind[0]+1)

    m = np.size(failed_ids)
    n = np.size(ranks)
    APFD = 100*(1 - sum/(m*n) + 1/(2*n))
    return APFD


