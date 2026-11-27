 # ============================================
# 步骤 12：Boss 符卡系统
# 目标：SpellCard 类、多个符卡、固定顺序按时间切换、右上角显示符卡名
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
        self.x = x
        self.y = y
        self.radius = 15           # 视觉模型半径（大圆）
        self.hitbox_radius = 3     # 判定点半径（小点，真正会受伤的）
        self.hp = 3                # 生命值
        self.respawn_timer = 0     # 0=正常，>0=重生动画中
        self.slow = False          # ← 新增：是否低速移动

    def update(self, keys):
        # 重生动画期间：只往上飞，不响应按键
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            self.y -= 4
            return                    # 提前返回，跳过下面的移动代码
        # 常速（小写 WASD）
        NORMAL = 4
        SLOW = 2
        if "a" in keys: self.x -= NORMAL
        if "d" in keys: self.x += NORMAL
        if "w" in keys: self.y -= NORMAL
        if "s" in keys: self.y += NORMAL
        # 低速（大写 = Shift + 字母）
        if "A" in keys: self.x -= SLOW
        if "D" in keys: self.x += SLOW
        if "W" in keys: self.y -= SLOW
        if "S" in keys: self.y += SLOW
        # 是否低速（给半透明和弹幕变窄用）
        self.slow = "A" in keys or "D" in keys or "W" in keys or "S" in keys  # 空1：判断是否有大写 WASD
        # 边界限制
        self.x = max(self.radius, min(480 - self.radius, self.x))
        self.y = max(self.radius, min(640 - self.radius, self.y))

    def draw(self, canvas):
        if self.slow:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill="#2563A4", stipple="gray50")   # 空2：stipple 伪透明
        else:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill="#2563A4")
        # （下面的判定点小圆保持不变）
        # 判定点：灰白色小点（真实受击框）
        canvas.create_oval(self.x - self.hitbox_radius, self.y - self.hitbox_radius,
                           self.x + self.hitbox_radius, self.y + self.hitbox_radius,
                           fill="#cccccc")

class Bullet(Entity):
    def __init__(self, x, y, thin=False):
        self.x = x
        self.y = y
        self.radius = 1.5 if thin else 3
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

class EnemyBullet(Entity):
    """敌方子弹：朝某个方向飞（继承 Entity）"""

    def __init__(self, x, y, angle, speed=3):
        self.x = x
        self.y = y
        self.radius = 6
        self.alive = True
        # 速度分解：把「角度 + 速度」拆成水平 vx 和竖直 vy
        self.vx = math.cos(angle) * speed     # 空1：cos(angle) * speed
        self.vy = math.sin(angle) * speed     # 空2：sin(angle) * speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -20 or self.x > 500 or self.y < -20 or self.y > 660:
            self.alive = False

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="#ff66ff", outline="white")

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
        self.canvas.pack()
        self.player = Player(240, 320)
        self.boss = Boss(240, 100)
        self.bullets = []            # 存放所有子弹
        self.fire_timer = 0          # 发射冷却计时器
        self.enemy_bullets = []      # 存放敌方子弹
        self.boss_fire_timer = 0     # Boss 发射冷却计时器
        self.keys = set()            # 当前按着的键
        self.root.bind("<KeyPress>", self.on_press)
        self.root.bind("<KeyRelease>", self.on_release)
        self.game_loop()             # 启动循环（必须放在所有属性初始化之后！）

    def on_press(self, event):
        self.keys.add(event.keysym)

    def on_release(self, event):
        key = event.keysym
        self.keys.discard(key)
        if len(key) == 1:               # 单个字母：大小写都删，防止卡键
            self.keys.discard(key.lower())
            self.keys.discard(key.upper())

    def update(self):
        self.player.update(self.keys)
        self.boss.update()

        # ---- 按住 空格 连发：每 8 帧发一颗（冷却计时器）----
        self.fire_timer += 1
        if "space" in self.keys and self.fire_timer >= 8:
            self.fire_timer = 0
            self.bullets.append(Bullet(self.player.x, self.player.y - 15, thin=self.player.slow))

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
        # ---- Boss 发射自机狙：玩家重生期间不发弹，到位后继续 ----
        if self.player.respawn_timer <= 0:
            self.boss_fire_timer += 1
            if self.boss_fire_timer >= 30:
                self.boss_fire_timer = 0
                self.fire_aimed_bullet()

        for eb in self.enemy_bullets:
            eb.update()

        # ---- 敌弹打中判定点：玩家死亡 ----
        for eb in self.enemy_bullets:
            dx = eb.x - self.player.x
            dy = eb.y - self.player.y
            if dx*dx + dy*dy < (eb.radius + self.player.hitbox_radius) ** 2:   # 空2：玩家的判定点半径
                self.player.hp -= 1
                self.player.x = 240
                self.player.y = 680               # 移到屏幕底部外
                self.player.respawn_timer = 90    # 进入 90 帧重生动画
                self.enemy_bullets.clear()        # 清空所有敌弹
                self.bullets.clear()              # 清空玩家子弹
                self.boss_fire_timer = 0          # 重置 Boss 发射计时器
                break
          
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

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

        # 画敌方子弹
        for eb in self.enemy_bullets:
            eb.draw(self.canvas)


    def game_loop(self):
        self.canvas.delete("all")    # ① 先清屏
        self.update()                # ② 统一 update
        self.draw()                  # ③ 统一 draw
        self.root.after(16, self.game_loop)

    def fire_aimed_bullet(self):
        dx = self.player.x - self.boss.x
        dy = self.player.y - self.boss.y
        angle = math.atan2(dy, dx)    # 空3：math.atan2(dy, dx)
        self.enemy_bullets.append(EnemyBullet(self.boss.x, self.boss.y, angle, speed=3))

root = tk.Tk()
root.title("Boss 关")
game = Game(root)
root.mainloop()
