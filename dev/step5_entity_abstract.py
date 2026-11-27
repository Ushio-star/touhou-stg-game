# ============================================
# 步骤 5：抽象基类 Entity + 继承
# 目标：认识 ABC、@abstractmethod、继承（Player 继承 Entity）
# ============================================
from abc import ABC, abstractmethod
import tkinter as tk


class Entity(ABC):                     # ABC = Abstract Base Class（抽象基类）
    @abstractmethod                    # 标签：下面这个方法是"抽象的"（只定名字，不写内容）
    def update(self):
        pass                           # pass = "占个位，啥也不做"

    @abstractmethod
    def draw(self, canvas):
        pass


class Player(Entity):
    """玩家类（一张"图纸"）"""

    def __init__(self, x, y):
        # 初始化：创建玩家对象时自动执行，把属性存好
        self.x = x
        self.y = y
        self.radius = 10

    def update(self, keys):
        """根据按下的键移动玩家（并限制边界）"""
        SPEED = 4
        if "Left" in keys or "a" in keys:  self.x -= SPEED
        if "Right" in keys or "d" in keys: self.x += SPEED
        if "Up" in keys or "w" in keys:    self.y -= SPEED
        if "Down" in keys or "s" in keys:  self.y += SPEED
        # 边界限制：用 max/min 把坐标夹在屏幕内
        self.x = max(self.radius, min(480 - self.radius, self.x))
        self.y = max(self.radius, min(640 - self.radius, self.y))

    def draw(self, canvas):
        """把玩家画到画布上"""
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="red")


# ---- 下面是"使用"这张图纸 ----
root = tk.Tk()
root.title("类版本的玩家")
canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
canvas.pack()

player = Player(240, 320)        # 照着图纸，造出一个玩家对象（实例）
keys = set()


def on_press(event):
    keys.add(event.keysym)


def on_release(event):
    keys.discard(event.keysym)


root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)


def game_loop():
    canvas.delete("all")
    player.update(keys)           # 让玩家自己更新（移动）
    player.draw(canvas)           # 让玩家自己画出来
    root.after(16, game_loop)


game_loop()
root.mainloop()
