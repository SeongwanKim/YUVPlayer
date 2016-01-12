"""BD-PSNR계산하는 코드"""
import numpy as np

def pchipend(h1, h2, del1, del2):
    """ pchip interpolation 끝부분"""
    d = ((2 * h1 + h2) * del1 - h1 * del2) / (h1 + h2)
    if d * del1 < 0:
        d = 0
    elif (del1 * del2 < 0) and (abs(d) > abs(3 * del1)):
        d = 3 * del1
    return d

def bdr_int(rate, dist, low, high):
    """BD-rate calculation main code"""
    rate = rate[-1::-1]
    dist = dist[-1::-1]
    rate = np.log10(rate)
    H = np.diff(dist)
    delta = np.divide(np.diff(rate), H)
    d = np.empty(4)
    d[0] = pchipend(H[0], H[1], delta[0], delta[1])
    d[1] = (3 * H[0] + 3 * H[1]) / ((2 * H[1] + H[0]) / delta[0] + (H[1] + 2 * H[0]) / delta[1])
    d[2] = (3 * H[1] + 3 * H[2]) / ((2 * H[2] + H[1]) / delta[1] + (H[2] + 2 * H[1]) / delta[2])
    d[3] = pchipend(H[2], H[1], delta[2], delta[1])

    c = np.empty(3)
    b = np.empty(3)
    for i in range(3):
        c[i] = (3 * delta[i] - 2 * d[i] - d[i+1]) / H[i]
        b[i] = (d[i] - 2 * delta[i] + d[i+1]) / (H[i] * H[i])
    result = 0
    for i in range(3):
        s0 = dist[i]
        s1 = dist[i+1]

        #' clip s0 to valid range
        s0 = max(s0, low)
        s0 = min(s0, high)

        #' clip s1 to valid range
        s1 = max(s1, low)
        s1 = min(s1, high)

        s0 = s0 - dist[i]
        s1 = s1 - dist[i]

        if s1 > s0:
            result = result + (s1 - s0) * rate[i]
            result = result + (s1 * s1 - s0 * s0) * d[i] / 2
            result = result + (s1 * s1 * s1 - s0 * s0 * s0) * c[i] / 3
            result = result + (s1 * s1 * s1 * s1 - s0 * s0 * s0 * s0) * b[i] / 4
    return result

def PSNR(ref):
    """ [rate_ref  dist_ref  rate_exp  dist_exp ] """
    rate_ref = ref[:, 0]
    dist_ref = ref[:, 1]
    rate_exp = ref[:, 2]
    dist_exp = ref[:, 3]

    min_dist = max(np.min(dist_ref), np.min(dist_exp))
    max_dist = min(np.max(dist_ref), np.max(dist_exp))
    vB = bdr_int(rate_exp, dist_exp, min_dist, max_dist)
    vA = bdr_int(rate_ref, dist_ref, min_dist, max_dist)
    avg = (vB - vA) / (max_dist - min_dist)
    return pow(10, avg)-1

def comp(fn1, fn2):
    """compare two summary.txt"""
    ref = ()
    exp = ()
    try:
        with open(fn1, 'r') as fp1:
            ref = fp1.readlines()
        with open(fn2, 'r') as fp2:
            exp = fp2.readlines()
    except Exception as e:
        import os
        print(os.getcwd())
        print(e.args[0])

    # validate
    if len(ref) != len(exp):
        return 10000

    cnt = 0
    sum = 0
    for i in range(0, len(ref), 4):
        ee = np.empty([4, 4])
        for j in range(4):
            r = ref[i+j].split()
            e = exp[i+j].split()
            if len(r) <= 2 or len(e) <= 2:
                return 10000
            ee[j, :] = [float(r[0]), float(r[1]), float(e[0]), float(e[1])]
        sum += PSNR(ee)
        cnt += 1
    return sum / cnt

if __name__ == '__main__':
    base_path = 'exp_old_00_result.txt'
    import glob
    for fn in glob.glob('*.txt'):
        avg_re = comp(base_path, fn)
        print(fn + '\t{0:2.2f}'.format(avg_re * 100))
