# 碰撞檢測工具函數


# 計算兩個向量的點積
def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


# 將多邊形投影到一個軸上，返回最小和最大值
def project(polygon, axis):
    dots = [dot(p, axis) for p in polygon]
    return min(dots), max(dots)


# 限制值在指定範圍內
def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))


# 正規化向量
def normalize(v):
    length = (v[0] ** 2 + v[1] ** 2) ** 0.5
    return (v[0] / length, v[1] / length)


# 獲取多邊形的所有法向量（軸）
def get_axes(polygon):
    axes = []
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = normalize((-edge[1], edge[0]))  # 法向量
        axes.append(normal)
    return axes


# 計算點到線段的距離
def point_to_segment_distance(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5


# 判斷點是否在凸多邊形內
def point_in_convex_polygon(point, polygon):
    sign = None

    def cross(a, b, c):
        ab = (b[0] - a[0], b[1] - a[1])
        ac = (c[0] - a[0], c[1] - a[1])
        return ab[0] * ac[1] - ab[1] * ac[0]

    for i in range(len(polygon)):
        a, b = polygon[i], polygon[(i + 1) % len(polygon)]
        cp = cross(a, b, point)
        if cp != 0:
            if sign is None:
                sign = cp > 0
            elif (cp > 0) != sign:
                return False
    return True


# 將矩形轉換為多邊形
def rect_to_polygon(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


# 判斷多邊形與多邊形、圓形、矩形之間的碰撞


# 判斷多邊形與多邊形之間的碰撞
def polygon_vs_polygon(p1, p2):
    for polygon in (p1, p2):
        for axis in get_axes(polygon):
            min1, max1 = project(p1, axis)
            min2, max2 = project(p2, axis)
            if max1 < min2 or max2 < min1:
                return False
    return True


# 判斷多邊形與圓形之間的碰撞
def polygon_vs_circle(polygon, center, radius):
    cx, cy = center
    if point_in_convex_polygon(center, polygon):
        return True
    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        dist = point_to_segment_distance(cx, cy, x1, y1, x2, y2)
        if dist <= radius:
            return True
    return False


# 判斷多邊形與矩形之間的碰撞
def polygon_vs_rect(polygon, rect):
    rect_poly = rect_to_polygon(rect)
    return polygon_vs_polygon(polygon, rect_poly)


# 判斷圓形與圓形之間的碰撞
def circle_vs_circle(center1, radius1, center2, radius2):
    dx = center2[0] - center1[0]
    dy = center2[1] - center1[1]
    dist_squared = dx * dx + dy * dy
    radius_sum = radius1 + radius2
    return dist_squared <= radius_sum * radius_sum


# 判斷圓形與矩形之間的碰撞
def rect_vs_circle(rect, center, radius):
    rx, ry, rw, rh = rect
    cx, cy = center

    # 找出離圓心最近的點
    closest_x = clamp(cx, rx, rx + rw)
    closest_y = clamp(cy, ry, ry + rh)

    # 計算最近點到圓心的距離
    dx = cx - closest_x
    dy = cy - closest_y
    return dx * dx + dy * dy <= radius * radius


# 判斷矩形與矩形之間的碰撞
def rect_vs_rect(r1, r2):
    return r1.colliderect(r2)
