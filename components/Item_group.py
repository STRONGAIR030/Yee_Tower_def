from abc import ABC, abstractmethod
from typing import List


class Item(ABC):
    def __init__(self, group=None):
        self.hit_box = None
        self.group: "ItemGroup" = None  # ItemGroup 的實例
        self.pos = [0, 0]  # 預設位置

    @abstractmethod
    def update(self, dt):
        pass  # 更新邏輯可以在子類中實現

    @abstractmethod
    def draw(self, surface, zoom):
        pass  # 繪製邏輯可以在子類中實現

    def kill(self):
        if self.group is not None:
            self.group.remove(self)
        else:
            print("No group to remove from")
        print("Item killed")
        # 在這裡可以添加更多邏輯，例如增加分數或播放音效


class ItemGroup:
    def __init__(self):
        self.group: List["Item"] = []

    def add(self, item: "Item"):
        self.group.append(item)
        item.group = self

    def remove(self, item: "Item"):
        if item not in self.group:
            print("Item not found in group")
            return
        self.group.remove(item)

    def update(self, dt):
        for item in self.group:
            item.update(dt)

    def __len__(self):
        return len(self.group)

    def __iter__(self):
        return iter(self.group)
