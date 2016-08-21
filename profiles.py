def linInterp(p1, p2, x):
    x1, y1 = p1
    x2, y2 = p2

    return y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)


def roundNearest(x, n):
    return int((x / n)) * n


def applyGraph(graph, temp):
    temps = [t for (t, _) in graph]

    if temp <= temps[0]:
        return graph[0][1]

    tempindex = -1
    for i, t in enumerate(temps):
        if temp < t:
            tempindex = i
            break

    if tempindex == -1:
        return graph[-1][1]
    else:
        return linInterp(graph[i - 1], graph[i], temp)


def normal(temp):
    graph = [(32, 100),
             (40, 160),
             (48, 240)]
    return roundNearest(applyGraph(graph, temp), 5)


def low(temp):
    graph = [(32, 100),
             (40, 130),
             (48, 185)]
    return roundNearest(applyGraph(graph, temp), 5)
