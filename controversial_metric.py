import math

scores = [(1,1), (105, 100),(107, 100), (110, 100), (120, 100), \
(130,100),(1,0), (1,2),(1001, 1000), (101, 100), (102, 100), (103, 100), \
(104,100),(99, 100), (999, 1000), (100,100), (100, 130), (100, 150), (1000, 700)]

def controversial_metric(up, down):
    match = min(up, down)
    top = match * math.log(match + 1)
    bottom = abs(up - down) + 1
    return float(top) / bottom

l = []
for up, down in scores:
    l.append((up, down, controversial_metric(up, down)))

l = sorted(l, key=lambda x : x[2], reverse=True)
for i in l:
    print(i)
