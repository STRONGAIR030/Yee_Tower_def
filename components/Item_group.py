from abc import ABC, abstractmethod
from typing import List


# 用於管理可以刪除的物品的基礎類別
class Item(ABC):
    def __init__(self, group=None):
        self.hit_box = None  # 碰撞檢測方式，可能是 "circle", "rect", "polygon" 等
        self.group: "ItemGroup" = None  # ItemGroup 的實例
        self.pos = [0, 0]  # 預設位置

    @abstractmethod
    def update(self, dt):
        pass  # 更新邏輯可以在子類中實現

    @abstractmethod
    def draw(self, surface, zoom):
        pass  # 繪製邏輯可以在子類中實現

    def kill(self):  # 刪除物品
        if self.group is not None:
            self.group.remove(self)
        else:
            print("No group to remove from")
        # print("Item killed")
        # 在這裡可以添加更多邏輯，例如增加分數或播放音效


class ItemGroup:  # 用於管理一組 Item 的類別
    def __init__(self):
        self.group: List["Item"] = []

    def add(self, item: "Item"):  # 添加 Item 到組中
        self.group.append(item)
        item.group = self

    def remove(self, item: "Item"):  # 從組中移除 Item
        if item not in self.group:
            print("Item not found in group")
            return
        self.group.remove(item)

    def update(self, dt):  # 更新組中所有 Item 的狀態
        for item in self.group:
            item.update(dt)

    def __len__(self):  # 返回組中 Item 的數量
        return len(self.group)

    def __iter__(self):  # 使 ItemGroup 可迭代
        return iter(self.group)
