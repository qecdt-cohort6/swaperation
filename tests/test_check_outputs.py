"""
These are handwritten tests to check the functions in `check_outputs.py`.
"""


from tests.check_outputs import cnot, swap, check_unitaries


def test_check_unitaries():
    ua = cnot(2, 3, 4) @ cnot(0, 3, 4) @ cnot(1, 0, 4)
    ub = cnot(3, 0, 4) @ cnot(2, 0, 4) @ cnot(1, 2, 4)
    uc = cnot(0, 1, 4) @ swap(4, (1, 3)) @ cnot(2, 3, 4) @ cnot(1, 2, 4) @ swap(4, (0, 2))
    ud = cnot(1, 3, 4) @ cnot(2, 3, 4) @ swap(4, (1, 3)) @ cnot(0, 2, 4) @ swap(4, (0, 1))
    ue = cnot(2, 0, 4) @ swap(4, (1, 2)) @ cnot(2, 0, 4) @ swap(4, (1, 0)) @ cnot(3, 2, 4)
    uf = cnot(2, 3, 4) @ swap(4, (0, 2)) @ cnot(2, 3, 4) @ swap(4, (1, 3)) @ cnot(3, 2, 4)

    pb = [3, 1, 0, 2]
    pc = [0, 1, 2, 3]
    pd = [3, 1, 0, 2]
    pe = [2, 3, 0, 1]
    pf = [2, 3, 0, 1]

    fb = [3, 1, 0, 2]
    fc = [2, 3, 0, 1]
    fd = [1, 2, 0, 3]
    fe = [3, 0, 2, 1]
    ff = [0, 1, 2, 3]
    assert(check_unitaries(ua, ub, pb, fb, 4))
    assert(check_unitaries(ua, uc, pc, fc, 4))
    assert(check_unitaries(ua, ud, pd, fd, 4))
    assert(check_unitaries(ua, ue, pe, fe, 4))
    assert(check_unitaries(ua, uf, pf, ff, 4))


if __name__ == '__main__':
    test_check_unitaries()
