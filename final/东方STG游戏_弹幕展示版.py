 # ============================================
# 东方 STG 弹幕游戏 —— 弹幕展示版（观看完整弹幕，无死亡机制）
# 包含全部答辩功能：移动/射击/低速/判定点/Boss/5种符卡弹幕/
#                  碰撞/死亡重生/胜负结算/Bomb/擦弹/三种道具/得分结算
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
        # 符卡系统
        self.spell_cards = [AimSpellCard(), CircleSpellCard(), SplitSpellCard(),BigBulletSpellCard(), DenseSpellCard()]
        self.current = 0                        # 当前符卡下标
        self.spell_name = self.spell_cards[0].name

    def update(self, player, enemy_bullets):
        self.timer += 1
        self.x = 240 + 150 * math.sin(self.timer * 0.015)

        # 玩家重生期间，符卡暂停（休整期）
        if player.respawn_timer > 0:
            return

        # 固定顺序、按时间切换符卡
        card = self.spell_cards[self.current]
        if card.timer >= card.duration:
            self.current =(self.current + 1) % len(self.spell_cards)           # 空2：切到下一个，用取模实现循环
            card = self.spell_cards[self.current]
            card.timer = 0
        self.spell_name = card.name
        card.update(self, player, enemy_bullets)    

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
        self.hitbox_radius = self.radius    # ← 新增：碰撞判定半径（默认=视觉半径）

    @classmethod
    def aimed(cls, boss, player, speed=3):
        """类方法：创建一颗瞄准玩家的子弹（cls 会随调用方变成对应子类）"""
        dx = player.x - boss.x
        dy = player.y - boss.y
        angle = math.atan2(dy, dx)
        return cls(boss.x, boss.y, angle, speed)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -20 or self.x > 500 or self.y < -20 or self.y > 660:
            self.alive = False

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="#ff66ff", outline="white")
class SplitBullet(EnemyBullet):
    """分裂子弹：飞行一段距离后分裂成 3 颗小子弹"""

    def __init__(self, x, y, angle, speed=2.5, splits_left=999999):
        super().__init__(x, y, angle, speed)
        self.speed = speed
        self.splits_left = splits_left   # 还能再分裂几次
        self.distance_traveled = 0       # 已飞行距离
        self.has_split = False           # 是否已分裂

    def update(self):
        self.distance_traveled += self.speed    # 累加飞行距离
        super().update()                         # 调用父类：移动 + 出屏判定
        # 飞够 100 距离 + 还有分裂次数 + 本次没分裂过 → 分裂
        if self.splits_left > 0 and self.distance_traveled > 100 and not self.has_split:
            self.has_split = True
            self.alive = False                   # 母体消失
            angle = math.atan2(self.vy, self.vx)  # 当前飞行方向
            # 子体继承「剩余分裂次数 - 1」
            return [SplitBullet(self.x, self.y, angle + i * 0.35, speed=2.5,
                                splits_left=self.splits_left - 1) for i in [-1, 0, 1]]
        return []                                # 没分裂：返回空列表

class BigBullet(EnemyBullet):
    """大玉：大子弹，只有内部核心有判定"""

    def __init__(self, x, y, angle, speed=2):
        super().__init__(x, y, angle, speed)
        self.radius = 48            # 视觉大圆半径
        self.core_radius = 12        # 内部核心半径
        self.hitbox_radius = self.core_radius   # 碰撞检测用核心半径（不是 18）

    def draw(self, canvas):
        # 外圈：白色大圆
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="#e96363")
        # 内部核心：红色小圆（只有它能打中玩家）
        canvas.create_oval(self.x - self.core_radius, self.y - self.core_radius,
                           self.x + self.core_radius, self.y + self.core_radius,
                           fill="#ff3333")   # 空1：用 self.core_radius 画红色核心，fill="#ff3333"
        
class SpellCard:
    """符卡基类：一种弹幕模式（像角色的技能）"""

    def __init__(self, name, duration):
        self.name = name          # 符卡名
        self.duration = duration  # 持续多少帧
        self.timer = 0            # 本符卡已进行几帧

    def update(self, boss, player, enemy_bullets):
        """发射弹幕（子类重写），顺便计时"""
        self.timer += 1

class AimSpellCard(SpellCard):
    """符卡1：自机狙（瞄准玩家）"""

    def __init__(self):
        super().__init__("自机狙「瞄准射击」", duration=300)   # 300帧 = 5秒
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)   # 调用父类计时
        self.fire_timer += 1
        if self.fire_timer >= 30:
            self.fire_timer = 0
            enemy_bullets.append(EnemyBullet.aimed(boss, player, speed=5))


class CircleSpellCard(SpellCard):
    """符卡2：圆形弹（向四周发射一圈）"""

    def __init__(self):
        super().__init__("圆形弹「全向开花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 40:
            self.fire_timer = 0
            for i in range(16):                          # 12 发一圈
                angle = i * math.pi / 8                  # 空1：每 30° 一发（用弧度）
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=2.5))

class SplitSpellCard(SpellCard):
    """符卡3：分裂弹"""

    def __init__(self):
        super().__init__("分裂弹「三开花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 60:                 # 每 60 帧发一颗
            self.fire_timer = 0
            enemy_bullets.append(SplitBullet.aimed(boss, player, speed=2.5))

class BigBulletSpellCard(SpellCard):
    """符卡4：大玉"""

    def __init__(self):
        super().__init__("大玉「核心冲击」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 90:                 # 每 90 帧发一颗
            self.fire_timer = 0
            for i in range(6):
                offset = (i - 2.5) * 0.2   # 6 颗大玉扇形散开
                dx = player.x - boss.x
                dy = player.y - boss.y
                angle = math.atan2(dy, dx) + offset
                enemy_bullets.append(BigBullet(boss.x, boss.y, angle, speed=1.5))

class DenseSpellCard(SpellCard):
    """符卡5：高密度扇形扫射（变向演出）"""

    def __init__(self):
        super().__init__("高密度「扇形扫射」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        # 扫射中心角度：朝下（pi/2），左右来回摆动 = 变向
        sweep = math.pi / 2 + math.sin(self.timer * 0.04) * 0.7  # 空1：朝下 + 左右摆动
        if self.fire_timer >= 4:            # 每 12 帧一波（高密度）
            self.fire_timer = 0
            for i in range(-5, 6):          # 11 发铺成扇形
                angle = sweep + i * math.pi / 12  # 空2：sweep + 偏移
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=3))

class Item(Entity):
    """掉落道具：不同类型有不同效果"""

    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.size = 10
        self.alive = True
        self.kind = kind   # "shield" / "speed" / "bomb"

    def update(self):
        self.y += 2              # 缓慢下落
        if self.y > 660:
            self.alive = False

    def draw(self, canvas):
        color = {"shield": "#44ccff", "speed": "#ffaa00", "bomb": "#00ff88"}[self.kind]
        canvas.create_rectangle(self.x - self.size, self.y - self.size,
                                self.x + self.size, self.y + self.size,
                                fill=color, outline="white")


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
        self.keys = set()            # 当前按着的键
        self.game_state = "playing"
        self.bomb_count = 2           # 剩余炸弹数
        self.invincible_timer = 0     # 无敌帧数
        self.bomb_cooldown = 0        # 冷却帧数
        self.graze = 0                # 擦弹得分
        self.items = []               # 掉落道具列表
        self.shield = False           # 护盾（一次性免伤）
        self.speed_boost_timer = 0    # 攻速加成剩余帧数
        # 掉道具阈值 = Boss 最大血量的 75% / 50% / 25%（按百分比算，可自定义）
        self.drop_thresholds = [int(self.boss.max_hp * 0.75),
                                int(self.boss.max_hp * 0.50),
                                int(self.boss.max_hp * 0.25)]
        self.drop_kinds = ["shield", "speed", "bomb"]
        self.drop_index = 0
        self.elapsed_frames = 0      # 游戏用时（帧数）
        self.root.bind("<KeyPress>", self.on_press)
        self.root.bind("<KeyRelease>", self.on_release)
        self.game_loop()             # 启动循环（必须放在所有属性初始化之后！）

    def on_press(self, event):
        self.keys.add(event.keysym)
        if event.keysym.lower() == "x":   # 按 X 触发 Bomb（大小写都认）
            self.try_bomb()

    def on_release(self, event):
        key = event.keysym
        self.keys.discard(key)
        if len(key) == 1:               # 单个字母：大小写都删，防止卡键
            self.keys.discard(key.lower())
            self.keys.discard(key.upper())

    def try_bomb(self):
        if self.bomb_count > 0 and self.bomb_cooldown == 0:
            self.bomb_count -= 1
            self.enemy_bullets.clear()      # 清屏所有敌弹
            self.invincible_timer = 180     # 3 秒无敌
            self.bomb_cooldown = 600        # 10 秒冷却

    def update(self):
        self.elapsed_frames += 1    # 累计用时

        # 递减无敌和冷却计时
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1

        self.player.update(self.keys)
        self.boss.update(self.player, self.enemy_bullets)

        # ---- 按住 空格 连发：每 8 帧发一颗（冷却计时器）----
        fire_interval = 4 if self.speed_boost_timer > 0 else 8   # 攻速加成时射击间隔减半
        self.fire_timer += 1
        if "space" in self.keys and self.fire_timer >= fire_interval:
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
                if self.boss.hp <= 0:          # Boss 血条归零 → 胜利
                    self.game_state = "win"
                # 掉道具：血条低于阈值且还有道具没掉
                if (self.drop_index < len(self.drop_thresholds)
                        and self.boss.hp <= self.drop_thresholds[self.drop_index]):
                    self.items.append(Item(self.boss.x, self.boss.y, self.drop_kinds[self.drop_index]))
                    self.drop_index += 1

        self.bullets = [b for b in self.bullets if b.alive]

        # 更新敌方子弹（并收集分裂出的子子弹）
        new_bullets = []
        for eb in self.enemy_bullets:
            children = eb.update()      # 分裂弹会返回子子弹，普通敌弹返回 None
            if children:
                new_bullets.extend(children)
        self.enemy_bullets.extend(new_bullets)

                # （展示版：已删除死亡机制，玩家不会死亡）

# ---- 擦弹判定：与视觉模型重合但没中判定点 ----
        for eb in self.enemy_bullets:
            dx = eb.x - self.player.x
            dy = eb.y - self.player.y
            dist2 = dx*dx + dy*dy
            if (eb.hitbox_radius + self.player.hitbox_radius) ** 2 <= dist2 < (eb.radius + self.player.radius) ** 2:
                self.graze += 1

        # ---- 道具：更新 + 玩家拾取 ----
        for it in self.items:
            it.update()
        for it in self.items:
            dx = it.x - self.player.x
            dy = it.y - self.player.y
            if dx*dx + dy*dy < (it.size + self.player.radius) ** 2:
                it.alive = False
                if it.kind == "shield":
                    self.shield = True
                elif it.kind == "speed":
                    self.speed_boost_timer = 180
                elif it.kind == "bomb":
                    self.bomb_count += 1
        self.items = [it for it in self.items if it.alive]

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

        self.canvas.create_text(470, 30, anchor="ne",
                                text=self.boss.spell_name,
                                fill="white", font=("Arial", 14, "bold"))
        # 画掉落道具
        for it in self.items:
            it.draw(self.canvas)

        # HUD：擦弹 + 炸弹
        self.canvas.create_text(10, 40, anchor="nw", text=f"擦弹: {self.graze}", fill="white")
        if self.bomb_cooldown > 0:
            self.canvas.create_text(10, 60, anchor="nw",
                                    text=f"Bomb: {self.bomb_count}（冷却 {(self.bomb_cooldown + 59) // 60}s）",
                                    fill="#888888")
        else:
            self.canvas.create_text(10, 60, anchor="nw", text=f"Bomb: {self.bomb_count}", fill="white")
        self.canvas.create_text(10, 80, anchor="nw", text=f"时间: {self.elapsed_frames // 60}s", fill="white")

        if self.game_state == "win":
            self.draw_settlement()
        elif self.game_state == "lose":
            self.canvas.create_text(240, 320, text="Game Over",
                                    fill="#ff3333", font=("Arial", 40, "bold"))
                    
    def draw_settlement(self):
        """胜利结算界面：总得分 + 各项得分 + 等第"""
        # 各项得分（数值可自行调整）
        graze_score = self.graze * 10            # 擦弹得分（每次擦弹 10 分）
        life_score = self.player.hp * 10000      # 剩余生命得分（每条命 10000 分）
        time_score = max(0, 60000 - self.elapsed_frames * 10)   # 用时得分（越快越高）
        bomb_score = self.bomb_count * 5000      # 剩余 Bomb 得分（每个 5000 分）
        total = graze_score + life_score + time_score + bomb_score

        # 等第（按总得分划分）
        if total >= 80000:
            grade = "S"
        elif total >= 60000:
            grade = "A"
        elif total >= 40000:
            grade = "B"
        else:
            grade = "C"

        self.canvas.create_text(240, 180, text="Stage Clear", fill="#ffcc00", font=("Arial", 36, "bold"))
        self.canvas.create_text(240, 250, text=f"总得分 {total}", fill="white", font=("Arial", 30, "bold"))
        self.canvas.create_text(240, 300, text=f"擦弹得分：{graze_score}", fill="white", font=("Arial", 15))
        self.canvas.create_text(240, 322, text=f"剩余生命得分：{life_score}", fill="white", font=("Arial", 15))
        self.canvas.create_text(240, 344, text=f"用时得分：{time_score}", fill="white", font=("Arial", 15))
        self.canvas.create_text(240, 366, text=f"剩余Bomb得分：{bomb_score}", fill="white", font=("Arial", 15))
        self.canvas.create_text(240, 410, text=f"等第：{grade}", fill="#ffcc00", font=("Arial", 34, "bold"))

    def game_loop(self):
        self.canvas.delete("all")
        if self.game_state == "playing":     # 只有游戏中才 update
            self.update()
        self.draw()
        if self.game_state == "playing":     # 只有游戏中才继续预约下一帧
            self.root.after(16, self.game_loop)

root = tk.Tk()
root.title("Boss 关")
game = Game(root)
root.mainloop()
