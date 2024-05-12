import time
import random
N, X, Y, Z = map(int, input().split())

k = random.randint(0, 3)
if k == 0:
    raise NotImplementedError("This is a placeholder")
elif k == 1:
    time.sleep(2)
elif k == 2:
    exit(2)
else:
    print("Yes" if (X <= Z <= Y) or (X >= Z >= Y) else "No")