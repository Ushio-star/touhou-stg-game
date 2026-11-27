# ============================================
# 步骤 8：子弹打中 Boss 掉血（碰撞检测）
# 目标：圆形碰撞检测、子弹打 Boss 掉血、血条下降
# ============================================
from abc import ABC, abstractmethod
import tkinter as tk
import math


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
                           fill="#2563A4")


class Bullet(Entity):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 3
        self.alive = True        # 子弹"活着"吗？（飞出屏幕就"死"）

    def update(self):
        self.y -= 6              # 往上飞
        if self.y < -10:
            self.alive = False   # 飞出屏幕顶部，标记"死亡"

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="white")


class Boss(Entity):
    """Boss 类（敌人，也继承 Entity）"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.hp = 1000          # 当前血量
        self.max_hp = 1000      # 最大血量
        self.alive = True
        self.timer = 0          # 移动计时器

    def update(self):
        self.timer += 1
        # 中心 240，左右幅度 150（最左 90，最右 390）；sin 让移动平滑
        self.x = 240 + 150 * math.sin(self.timer * 0.015)

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="#b831ba")


class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
        self.canvas.pack()
        self.player = Player(240, 320)
        self.boss = Boss(240, 100)
        self.bullets = []            # 存放所有子弹
        self.fire_timer = 0          # 发射冷却计时器
        self.keys = set()            # 当前按着的键
        self.root.bind("<KeyPress>", self.on_press)
        self.root.bind("<KeyRelease>", self.on_release)
        self.game_loop()             # 启动循环（必须放在所有属性初始化之后！）

    def on_press(self, event):
        self.keys.add(event.keysym)

    def on_release(self, event):
        self.keys.discard(event.keysym)

    def update(self):
        self.player.update(self.keys)
        self.boss.update()

        # ---- 按住 空格 连发：每 8 帧发一颗（冷却计时器）----
        self.fire_timer += 1
        if "space" in self.keys and self.fire_timer >= 8:
            self.fire_timer = 0
            self.bullets.append(Bullet(self.player.x, self.player.y - 15))

        for b in self.bullets:
            b.update()

        for b in self.bullets:
            dx = b.x - self.boss.x
            dy = b.y - self.boss.y
            distance_squared = dx * dx + dy * dy
            if distance_squared < (b.radius + self.boss.radius) ** 2:   # 圆心距离² < 半径和²（省开方，更快）
                b.alive = False                              # 子弹消失
                self.boss.hp = max(0, self.boss.hp - 50)     # Boss 掉 50 血（最低到 0）

        self.bullets = [b for b in self.bullets if b.alive]

    def draw(self):
        self.player.draw(self.canvas)
        for b in self.bullets:
            b.draw(self.canvas)
        self.boss.draw(self.canvas)

        # ---- 顶部 Boss 血条 ----
        # 背景条（深灰，固定 400 宽）
        self.canvas.create_rectangle(40, 10, 440, 24, fill="#444444", outline="white")
        # 前景条（红色，宽度随血量变短）
        ratio = self.boss.hp / self.boss.max_hp
        self.canvas.create_rectangle(40, 10, 40 + 400 * ratio, 24, fill="#ff4444", outline="")

    def game_loop(self):
        self.canvas.delete("all")    # ① 先清屏
        self.update()                # ② 统一 update
        self.draw()                  # ③ 统一 draw
        self.root.after(16, self.game_loop)


root = tk.Tk()
root.title("Boss 关")
game = Game(root)
root.mainloop()
