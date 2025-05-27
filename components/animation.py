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
        self.delay = delay
        self.delay_time = delay
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")

        self.duration = duration
        self.start_value = start_value
        self.end_value = end_value
        self.easing_function = easing_function
        self.elapsed = 0.0
        self.repeat = repeat

    @property
    def ease_value(self) -> float:
        t = min(self.elapsed / self.duration, 1.0)
        if self.easing_function == "ease_in":
            return ease_in(t)
        elif self.easing_function == "ease_out":
            return ease_out(t)
        else:
            return ease_in_out(t)

    @property
    def value(self) -> float:
        return self.start_value + (self.end_value - self.start_value) * self.ease_value

    @property
    def is_complete(self) -> bool:
        return self.elapsed >= self.duration

    def update(self, dt: float) -> None:
        if self.delay_time > 0:
            self.delay_time -= dt
        else:
            if self.is_complete:
                if self.repeat > 0 or self.repeat == -1:
                    self.repeat -= 1
                    self.reset()
            else:
                self.elapsed += dt

    def reset(self) -> None:
        self.elapsed = 0.0
        self.delay_time = self.delay


class AnimationManager:
    def __init__(self, animation_array=[], repet: int = 0):
        self.animations: List["Animation"] = self.create_animation_list(animation_array)
        self.repeat = repet

    def create_animation_list(animation_array):
        animation_list = []
        delay = 0.0
        for animation in animation_array:
            delay += animation[5] if len(animation) > 5 else 0.0
            new_animation = Animation(
                duration=animation[0],
                start_value=animation[1],
                end_value=animation[2],
                delay=animation[3] if len(animation) > 5 else delay,
                repeat=animation[4] if len(animation) > 6 else 0,
                easing_function=animation[5] if len(animation) > 3 else "ease_in_out",
            )
            animation_list.append(new_animation)
        return animation_list

    @property
    def is_complete(self) -> bool:
        return all(animation.is_complete for animation in self.animations)

    def update(self, dt: float) -> None:
        for animation in self.animations:
            animation.update(dt)
            if self.is_complete:
                if self.repeat > 0 or self.repeat == -1:
                    animation.reset()
