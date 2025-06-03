from typing import List


def ease_in(t):  # 緩慢開始（加速度）
    return t * t


def ease_out(t):  # 緩慢結束（減速度）
    return 1 - (1 - t) * (1 - t)


def ease_in_out(t):  # 慢 -> 快 -> 慢
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)


# Animation 類別，用於處理動畫效果
class Animation:
    def __init__(
        self,
        duration: float,
        start_value: float,
        end_value: float,
        delay: float = 0.0,
        repeat: int = 0,
        easing_function: str = "ease",
    ):
        self.delay = delay  # 延遲開始時間
        self.delay_time = delay  # 剩餘延遲時間
        if duration <= 0:  # 檢查持續時間是否大於 0
            raise ValueError("Duration must be greater than 0")

        self.duration = duration  # 動畫持續時間
        self.start_value = start_value  # 動畫起始值
        self.end_value = end_value  # 動畫結束值
        self.easing_function = easing_function  # 緩動函數類型
        self.elapsed = 0.0  # 已經過的時間
        self.repeat = repeat  # 重複次數，-1 表示無限重複

    @property
    def ease_value(self) -> float:  # 計算緩動值
        t = min(self.elapsed / self.duration, 1.0)
        if self.easing_function == "ease_in":
            return ease_in(t)
        elif self.easing_function == "ease_out":
            return ease_out(t)
        else:
            return ease_in_out(t)

    @property
    def value(self) -> float:  # 計算當前動畫值
        return self.start_value + (self.end_value - self.start_value) * self.ease_value

    @property
    def is_complete(self) -> bool:  # 檢查動畫是否完成
        return self.elapsed >= self.duration

    def update(self, dt: float) -> None:  # 更新動畫狀態
        if self.delay_time > 0:
            self.delay_time -= dt
        else:
            if self.is_complete:  # 如果動畫已完成
                if self.repeat == -1:  # 無限重複
                    self.reset()
                elif self.repeat > 0:  # 有限重複
                    self.repeat -= 1
                    self.reset()
            else:
                self.elapsed += dt

    def reset(self) -> None:  # 重置動畫狀態
        self.elapsed = 0.0
        self.delay_time = self.delay


# AnimationManager 類別，用於管理連續動畫效果
class AnimationManager:
    def __init__(self, animation_array=[], repet: int = 0):
        self.animations: List["Animation"] = self.create_animation_list(
            list(animation_array)
        )
        self.repeat = repet  # 重複次數，-1 表示無限重複

    # 創建動畫列表，將動畫參數轉換為 Animation 對象
    def create_animation_list(self, animation_array: list):
        animation_list = []
        delay = 0.0
        for animation in animation_array:
            delay += animation[5] if len(animation) > 5 else 0.0
            new_animation = Animation(
                duration=animation[0],  # 動畫持續時間
                start_value=animation[1],  # 動畫起始值
                end_value=animation[2],  # 動畫結束值
                delay=animation[3] if len(animation) > 3 else delay,  # 延遲開始時間
                repeat=animation[4] if len(animation) > 4 else 0,  # 重複次數
                easing_function=animation[5]
                if len(animation) > 5
                else "ease_in_out",  # 緩動函數類型
            )
            animation_list.append(new_animation)  # 將 Animation 對象添加到列表中
        return animation_list

    @property
    def is_complete(self) -> bool:  # 檢查所有動畫是否完成
        return all(animation.is_complete for animation in self.animations)

    @property
    def value(self) -> List[float]:  # 獲取連續動畫的當前值
        value = 0
        for animation in self.animations:
            value = animation.value
            if not animation.is_complete:
                break
        return value

    def update(self, dt: float) -> None:  # 更新所有動畫狀態
        be_reset = False
        if self.is_complete and self.repeat == 0:  # 如果動畫已完成且不重複
            return
        elif self.is_complete and self.repeat == -1:  # 如果動畫已完成且無限重複
            be_reset = True
        elif self.is_complete and self.repeat > 0:  # 如果動畫已完成且有限重複
            self.repeat -= 1
            be_reset = True

        for animation in self.animations:  # 更新每個動畫
            animation.update(dt)
            if be_reset:
                animation.reset()
