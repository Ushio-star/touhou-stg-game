
from abc import ABC, abstractmethod
import tkinter as tk
import math
def ask_int(prompt, default):
    try:
        s = input(f"{prompt}（默认 {default}）：").strip()
        return int(s) if s else default
    except ValueError:
        print(f"  输入无效，使用默认值 {default}")
        return default

def ask_float(prompt, default):
    try:
        s = input(f"{prompt}（默认 {default}）：").strip()
        return float(s) if s else default
    except ValueError:
        print(f"  输入无效，使用默认值 {default}")
        return default

print("========== 东方 STG 弹幕游戏 · 自定义设置 ==========")
BOSS_MAX_HP = ask_int("Boss 血量", 1000)
PLAYER_HP = ask_int("玩家生命", 3)
PLAYER_SPEED_NORMAL = ask_float("玩家移动速度", 4)
PLAYER_SPEED_SLOW = ask_float("低速移动速度", 2)
BULLET_DAMAGE = ask_int("玩家子弹伤害", 50)
FIRE_INTERVAL = ask_int("射击间隔（越大子弹越慢）", 8)
BOMB_COUNT = ask_int("Bomb 数量", 2)
cancel_cooldown = ask_int("是否取消 Bomb 冷却时间（0=取消 1=保留）", 1)
if cancel_cooldown == 0:
    BOMB_COOLDOWN_FRAMES = 0
else:
    BOMB_COOLDOWN_FRAMES = ask_int("Bomb 冷却秒数", 10) * 60
SPLIT_COUNT = ask_int("分裂弹分裂次数", 2)
BIG_BULLET_COUNT = ask_int("大玉每次发射数量", 1)
AIMED_BULLET_SPEED = ask_float("自机狙子弹速度", 3)
DENSE_FIRE_INTERVAL = ask_int("高密度弹幕射击间隔（帧，越小越密）", 12)
print("========== 设置完成，游戏启动！ ==========\n")
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 640
BG_COLOR = "#000011"
PLAYER_RADIUS = 15
PLAYER_HITBOX_RADIUS = 3
PLAYER_COLOR = "#2563A4"
BULLET_SPEED = 6
BULLET_RADIUS = 3
BULLET_RADIUS_THIN = 1.5
FIRE_INTERVAL_FAST = 4
BOSS_RADIUS = 30
BOSS_COLOR = "#b831ba"
BOSS_MOVE_AMPLITUDE = 150
BOSS_MOVE_SPEED = 0.015
ENEMY_BULLET_RADIUS = 6
ENEMY_BULLET_COLOR = "#ff66ff"
BOMB_INVINCIBLE_FRAMES = 180
DROP_RATIOS = [0.75, 0.50, 0.25]
DROP_KINDS = ["shield", "speed", "bomb"]
SPEED_BOOST_FRAMES = 180
GRAZE_SCORE_PER = 10
LIFE_SCORE_PER = 10000
TIME_SCORE_BASE = 60000
TIME_SCORE_RATE = 10
BOMB_SCORE_PER = 5000
GRADE_S = 80000
GRADE_A = 60000
GRADE_B = 40000

class Entity(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, canvas):
        pass

class Player(Entity):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.hitbox_radius = PLAYER_HITBOX_RADIUS
        self.hp = PLAYER_HP
        self.respawn_timer = 0
        self.slow = False

    def update(self, keys):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            self.y -= 4
            return
        NORMAL = PLAYER_SPEED_NORMAL
        SLOW = PLAYER_SPEED_SLOW
        if "a" in keys: self.x -= NORMAL
        if "d" in keys: self.x += NORMAL
        if "w" in keys: self.y -= NORMAL
        if "s" in keys: self.y += NORMAL
        if "A" in keys: self.x -= SLOW
        if "D" in keys: self.x += SLOW
        if "W" in keys: self.y -= SLOW
        if "S" in keys: self.y += SLOW
        self.slow = "Shift_L" in keys or "Shift_R" in keys
        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))

    def draw(self, canvas):
        if self.slow:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill="#A1C9F4")
        else:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill=PLAYER_COLOR)
        canvas.create_oval(self.x - self.hitbox_radius, self.y - self.hitbox_radius,
                           self.x + self.hitbox_radius, self.y + self.hitbox_radius,
                           fill="#cccccc")

class Bullet(Entity):
    def __init__(self, x, y, thin=False):
        self.x = x
        self.y = y
        self.radius = BULLET_RADIUS_THIN if thin else BULLET_RADIUS
        self.alive = True

    def update(self):
        self.y -= BULLET_SPEED
        if self.y < -10:
            self.alive = False

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="white")

class Boss(Entity):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BOSS_RADIUS
        self.hp = BOSS_MAX_HP
        self.max_hp = BOSS_MAX_HP
        self.alive = True
        self.timer = 0
        self.spell_cards = [AimSpellCard(), CircleSpellCard(), SplitSpellCard(),BigBulletSpellCard(), DenseSpellCard()]
        self.current = 0
        self.spell_name = self.spell_cards[0].name

    def update(self, player, enemy_bullets):
        self.timer += 1
        self.x = WINDOW_WIDTH // 2 + BOSS_MOVE_AMPLITUDE * math.sin(self.timer * BOSS_MOVE_SPEED)
        if player.respawn_timer > 0:
            return
        card = self.spell_cards[self.current]
        if card.timer >= card.duration:
            self.current =(self.current + 1) % len(self.spell_cards)
            card = self.spell_cards[self.current]
            card.timer = 0
        self.spell_name = card.name
        card.update(self, player, enemy_bullets)    

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill=BOSS_COLOR)

class EnemyBullet(Entity):

    def __init__(self, x, y, angle, speed=3):
        self.x = x
        self.y = y
        self.radius = ENEMY_BULLET_RADIUS
        self.alive = True
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.hitbox_radius = self.radius

    @classmethod
    def aimed(cls, boss, player, speed=3):
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
                           fill=ENEMY_BULLET_COLOR, outline="white")
class SplitBullet(EnemyBullet):

    def __init__(self, x, y, angle, speed=2.5, splits_left=SPLIT_COUNT):
        super().__init__(x, y, angle, speed)
        self.speed = speed
        self.splits_left = splits_left
        self.distance_traveled = 0
        self.has_split = False

    def update(self):
        self.distance_traveled += self.speed
        super().update()
        if self.splits_left > 0 and self.distance_traveled > 100 and not self.has_split:
            self.has_split = True
            self.alive = False
            angle = math.atan2(self.vy, self.vx)
            return [SplitBullet(self.x, self.y, angle + i * 0.35, speed=2.5,
                                splits_left=self.splits_left - 1) for i in [-1, 0, 1]]
        return []

class BigBullet(EnemyBullet):

    def __init__(self, x, y, angle, speed=2):
        super().__init__(x, y, angle, speed)
        self.radius = 48
        self.core_radius = 12
        self.hitbox_radius = self.core_radius

    def draw(self, canvas):
        canvas.create_oval(self.x - self.radius, self.y - self.radius,
                           self.x + self.radius, self.y + self.radius,
                           fill="#e96363")
        canvas.create_oval(self.x - self.core_radius, self.y - self.core_radius,
                           self.x + self.core_radius, self.y + self.core_radius,
                           fill="#ff3333")
        
class SpellCard:

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.timer = 0

    def update(self, boss, player, enemy_bullets):
        self.timer += 1

class AimSpellCard(SpellCard):

    def __init__(self):
        super().__init__("自机狙「瞄准射击」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 30:
            self.fire_timer = 0
            enemy_bullets.append(EnemyBullet.aimed(boss, player, speed=AIMED_BULLET_SPEED))

class CircleSpellCard(SpellCard):

    def __init__(self):
        super().__init__("圆形弹「全向开花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 40:
            self.fire_timer = 0
            for i in range(12):
                angle = i * math.pi / 6
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=2.5))

class SplitSpellCard(SpellCard):

    def __init__(self):
        super().__init__("分裂弹「三开花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 60:
            self.fire_timer = 0
            enemy_bullets.append(SplitBullet.aimed(boss, player, speed=2.5))

class BigBulletSpellCard(SpellCard):

    def __init__(self):
        super().__init__("大玉「核心冲击」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 90:
            self.fire_timer = 0
            for i in range(BIG_BULLET_COUNT):
                offset = (i - (BIG_BULLET_COUNT - 1) / 2) * 0.2
                dx = player.x - boss.x
                dy = player.y - boss.y
                angle = math.atan2(dy, dx) + offset
                enemy_bullets.append(BigBullet(boss.x, boss.y, angle, speed=1.5))

class DenseSpellCard(SpellCard):

    def __init__(self):
        super().__init__("高密度「扇形扫射」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        sweep = math.pi / 2 + math.sin(self.timer * 0.04) * 0.7
        if self.fire_timer >= DENSE_FIRE_INTERVAL:
            self.fire_timer = 0
            for i in range(-5, 6):
                angle = sweep + i * math.pi / 12
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=3))

class Item(Entity):

    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.size = 10
        self.alive = True
        self.kind = kind

    def update(self):
        self.y += 2
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
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        self.player = Player(240, 320)
        self.boss = Boss(240, 100)
        self.bullets = []
        self.fire_timer = 0
        self.enemy_bullets = []
        self.keys = set()
        self.game_state = "playing"
        self.bomb_count = BOMB_COUNT
        self.invincible_timer = 0
        self.bomb_cooldown = 0
        self.graze = 0
        self.items = []
        self.shield = False
        self.speed_boost_timer = 0
        self.drop_thresholds = [int(self.boss.max_hp * r) for r in DROP_RATIOS]
        self.drop_kinds = ["shield", "speed", "bomb"]
        self.drop_index = 0
        self.elapsed_frames = 0
        self.root.bind("<KeyPress>", self.on_press)
        self.root.bind("<KeyRelease>", self.on_release)
        self.game_loop()

    def on_press(self, event):
        self.keys.add(event.keysym)
        if event.keysym.lower() == "x":
            self.try_bomb()
        if event.keysym.lower() == "o":
            self.game_state = "win"

    def on_release(self, event):
        key = event.keysym
        self.keys.discard(key)
        if len(key) == 1:
            self.keys.discard(key.lower())
            self.keys.discard(key.upper())

    def try_bomb(self):
        if self.bomb_count > 0 and self.bomb_cooldown == 0:
            self.bomb_count -= 1
            self.enemy_bullets.clear()
            self.invincible_timer = BOMB_INVINCIBLE_FRAMES
            self.bomb_cooldown = BOMB_COOLDOWN_FRAMES

    def update(self):
        self.elapsed_frames += 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1

        self.player.update(self.keys)
        self.boss.update(self.player, self.enemy_bullets)
        fire_interval = FIRE_INTERVAL_FAST if self.speed_boost_timer > 0 else FIRE_INTERVAL
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
            if distance_squared < (b.radius + self.boss.radius) ** 2:
                b.alive = False
                self.boss.hp = max(0, self.boss.hp - BULLET_DAMAGE)
                if self.boss.hp <= 0:
                    self.game_state = "win"
                if (self.drop_index < len(self.drop_thresholds)
                        and self.boss.hp <= self.drop_thresholds[self.drop_index]):
                    self.items.append(Item(self.boss.x, self.boss.y, self.drop_kinds[self.drop_index]))
                    self.drop_index += 1

        self.bullets = [b for b in self.bullets if b.alive]
        new_bullets = []
        for eb in self.enemy_bullets:
            children = eb.update()
            if children:
                new_bullets.extend(children)
        self.enemy_bullets.extend(new_bullets)
        for eb in self.enemy_bullets:
            dx = eb.x - self.player.x
            dy = eb.y - self.player.y
            if dx*dx + dy*dy < (eb.hitbox_radius + self.player.hitbox_radius) ** 2:
                if self.invincible_timer > 0:
                    continue
                if self.shield:
                    self.shield = False
                    self.enemy_bullets.clear()
                    break
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.game_state = "lose"
                    break                
                self.player.x = 240
                self.player.y = 680
                self.player.respawn_timer = 90
                self.enemy_bullets.clear()
                self.bullets.clear()
                break
        for eb in self.enemy_bullets:
            dx = eb.x - self.player.x
            dy = eb.y - self.player.y
            dist2 = dx*dx + dy*dy
            if (eb.hitbox_radius + self.player.hitbox_radius) ** 2 <= dist2 < (eb.radius + self.player.radius) ** 2:
                self.graze += 1
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
                    self.speed_boost_timer = SPEED_BOOST_FRAMES
                elif it.kind == "bomb":
                    self.bomb_count += 1
        self.items = [it for it in self.items if it.alive]

        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

    def draw(self):
        self.player.draw(self.canvas)
        for b in self.bullets:
            b.draw(self.canvas)
        self.boss.draw(self.canvas)
        self.canvas.create_rectangle(40, 10, 440, 24, fill="#444444", outline="white")
        ratio = self.boss.hp / self.boss.max_hp
        self.canvas.create_rectangle(40, 10, 40 + 400 * ratio, 24, fill="#ff4444", outline="")
        for eb in self.enemy_bullets:
            eb.draw(self.canvas)
        for it in self.items:
            it.draw(self.canvas)
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
        graze_score = self.graze * GRAZE_SCORE_PER
        life_score = self.player.hp * LIFE_SCORE_PER
        time_score = max(0, TIME_SCORE_BASE - self.elapsed_frames * TIME_SCORE_RATE)
        bomb_score = self.bomb_count * BOMB_SCORE_PER
        total = graze_score + life_score + time_score + bomb_score
        if total >= GRADE_S:
            grade = "S"
        elif total >= GRADE_A:
            grade = "A"
        elif total >= GRADE_B:
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
        if self.game_state == "playing":
            self.update()
        self.draw()
        if self.game_state == "playing":
            self.root.after(16, self.game_loop)

root = tk.Tk()
root.title("Boss 关")
game = Game(root)
root.mainloop()
