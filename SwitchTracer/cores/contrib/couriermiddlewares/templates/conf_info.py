import os
import hashlib
import numpy as np


def initial_conf_info(S, N=96, n=8):
    X = os.path.getsize(S)
    per = np.ceil(X / N).astype(np.int)
    rg = np.ceil(X / n).astype(np.int)
    rga = [rg for _ in range(n-1)]
    rga.append(X - (n-1) * rg)
    with open(S, 'rb') as f:
        mds = [hashlib.md5(f.read(i)).hexdigest() for i in rga]
    print(
        "Source = {}\nSize = {}\nBlocks = {}\nMemoryPerBlock = {}\nCheckBlocks = {}\nCheckMd5 = {}"
        .format(S, X, N, per, rga, mds)
    )
    return X, N, per, rga, mds


def initial_conf(S, I, mem, blk, spb, mcr, mds):
    with open(".template.conf", "r") as f:
        context = f.read()
    context = context.format(fname="Test_%s" % S, id=str(I), mem=mem, blk=blk, spb=spb, mcr=mcr, mds=mds)
    # TODO: TO BE REQUEST BODY
    conf = os.path.join(
        r"C:\izayoi\prj_veyon\VirtualVeyonST\veyon\PySwitchTracer\tests", ".download_%s.conf" % S
    )
    with open(conf, "w") as f:
        f.write(context)


if __name__ == '__main__':
    S = r"C:\izayoi\prj_veyon\VirtualVeyonST\veyon\PySwitchTracer\static\sources\2020092301.tar.gz"
    I = 101
    info = initial_conf_info(S)
    initial_conf("2020092301.tar.gz", I, *info)

    S = r"C:\izayoi\prj_veyon\VirtualVeyonST\veyon\PySwitchTracer\static\sources\Lisao.txt"
    I = 100
    info = initial_conf_info(S, n=3)
    initial_conf("LiSao.txt", I, *info)

