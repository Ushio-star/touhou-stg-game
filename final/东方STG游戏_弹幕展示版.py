
from abc import ABC, abstractmethod
import tkinter as tk
import math

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
        self.radius = 15
        self.hitbox_radius = 3
        self.hp = 3
        self.respawn_timer = 0
        self.slow = False

    def update(self, keys):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            self.y -= 4
            return
        NORMAL = 4
        SLOW = 2
        if "a" in keys: self.x -= NORMAL
        if "d" in keys: self.x += NORMAL
        if "w" in keys: self.y -= NORMAL
        if "s" in keys: self.y += NORMAL
        if "A" in keys: self.x -= SLOW
        if "D" in keys: self.x += SLOW
        if "W" in keys: self.y -= SLOW
        if "S" in keys: self.y += SLOW
        self.slow = "Shift_L" in keys or "Shift_R" in keys
        self.x = max(self.radius, min(480 - self.radius, self.x))
        self.y = max(self.radius, min(640 - self.radius, self.y))

    def draw(self, canvas):
        if self.slow:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill="#A1C9F4")
        else:
            canvas.create_oval(self.x - self.radius, self.y - self.radius,
                               self.x + self.radius, self.y + self.radius,
                               fill="#2563A4")
        canvas.create_oval(self.x - self.hitbox_radius, self.y - self.hitbox_radius,
                           self.x + self.hitbox_radius, self.y + self.hitbox_radius,
                           fill="#cccccc")

class Bullet(Entity):
    def __init__(self, x, y, thin=False):
        self.x = x
        self.y = y
        self.radius = 1.5 if thin else 3
        self.alive = True

    def update(self):
        self.y -= 6
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
        self.radius = 30
        self.hp = 1000
        self.max_hp = 1000
        self.alive = True
        self.timer = 0
        self.spell_cards = [AimSpellCard(), CircleSpellCard(), SplitSpellCard(), BigBulletSpellCard(), DenseSpellCard(), SpiralSpellCard(), RingSpellCard(), WaveSpellCard()]
        self.current = 0
        self.spell_name = self.spell_cards[0].name

    def update(self, player, enemy_bullets):
        self.timer += 1
        self.x = 240 + 150 * math.sin(self.timer * 0.015)
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
                           fill="#b831ba")

class EnemyBullet(Entity):

    def __init__(self, x, y, angle, speed=3):
        self.x = x
        self.y = y
        self.radius = 6
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
                           fill="#ff66ff", outline="white")
class SplitBullet(EnemyBullet):

    def __init__(self, x, y, angle, speed=2.5, splits_left=999999):
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
            for i in range(3):
                offset = (i - 1) * 0.12
                dx = player.x - boss.x
                dy = player.y - boss.y
                angle = math.atan2(dy, dx) + offset
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=10))

class CircleSpellCard(SpellCard):

    def __init__(self):
        super().__init__("圆形弹「全向开花」", duration=600)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 20:
            self.fire_timer = 0
            for i in range(32):
                angle = i * math.pi / 16
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=5))

class SplitSpellCard(SpellCard):

    def __init__(self):
        super().__init__("分裂弹「三开花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 60:
            self.fire_timer = 0
            enemy_bullets.append(SplitBullet.aimed(boss, player, speed=5))

class BigBulletSpellCard(SpellCard):

    def __init__(self):
        super().__init__("大玉「核心冲击」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 90:
            self.fire_timer = 0
            for i in range(2):
                offset = (i - 0.5) * 0.2
                dx = player.x - boss.x
                dy = player.y - boss.y
                angle = math.atan2(dy, dx) + offset
                enemy_bullets.append(BigBullet(boss.x, boss.y, angle, speed=4))

class DenseSpellCard(SpellCard):

    def __init__(self):
        super().__init__("高密度「扇形扫射」", duration=600)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        sweep = math.pi / 2 + math.sin(self.timer * 0.04) * 0.7
        if self.fire_timer >= 2:
            self.fire_timer = 0
            for i in range(-5, 6):
                angle = sweep + i * math.pi / 12
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=6))

class SpiralSpellCard(SpellCard):
    def __init__(self):
        super().__init__("螺旋「旋转弹幕」", duration=300)
        self.fire_timer = 0
        self.spiral_angle = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        self.spiral_angle += 0.25
        if self.fire_timer >= 3:
            self.fire_timer = 0
            enemy_bullets.append(EnemyBullet(boss.x, boss.y, self.spiral_angle, speed=4))
            enemy_bullets.append(EnemyBullet(boss.x, boss.y, self.spiral_angle + math.pi, speed=4))

class RingSpellCard(SpellCard):
    def __init__(self):
        super().__init__("环形「同心圆」", duration=300)
        self.fire_timer = 0
        self.ring_offset = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        self.ring_offset += 0.08
        if self.fire_timer >= 8:
            self.fire_timer = 0
            for i in range(24):
                angle = i * (2 * math.pi / 24) + self.ring_offset
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=3))

class WaveSpellCard(SpellCard):
    def __init__(self):
        super().__init__("波浪「浪花」", duration=300)
        self.fire_timer = 0

    def update(self, boss, player, enemy_bullets):
        super().update(boss, player, enemy_bullets)
        self.fire_timer += 1
        if self.fire_timer >= 6:
            self.fire_timer = 0
            for i in range(11):
                angle = math.pi / 2 + math.sin(self.timer * 0.05 + i * 0.4) * 0.7
                enemy_bullets.append(EnemyBullet(boss.x, boss.y, angle, speed=3.5))

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
        self.canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
        self.canvas.pack()
        self.player = Player(240, 320)
        self.boss = Boss(240, 100)
        self.bullets = []
        self.fire_timer = 0
        self.enemy_bullets = []
        self.keys = set()
        self.game_state = "playing"
        self.bomb_count = 2
        self.invincible_timer = 0
        self.bomb_cooldown = 0
        self.graze = 0
        self.items = []
        self.shield = False
        self.speed_boost_timer = 0
        self.drop_thresholds = [int(self.boss.max_hp * 0.75),
                                int(self.boss.max_hp * 0.50),
                                int(self.boss.max_hp * 0.25)]
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
            self.invincible_timer = 180
            self.bomb_cooldown = 600

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
        fire_interval = 4 if self.speed_boost_timer > 0 else 8
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
                self.boss.hp = max(0, self.boss.hp - 50)
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
        graze_score = self.graze * 10
        life_score = self.player.hp * 10000
        time_score = max(0, 60000 - self.elapsed_frames * 10)
        bomb_score = self.bomb_count * 5000
        total = graze_score + life_score + time_score + bomb_score
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
        if self.game_state == "playing":
            self.update()
        self.draw()
        if self.game_state == "playing":
            self.root.after(16, self.game_loop)

root = tk.Tk()
root.title("Boss 关")
game = Game(root)
root.mainloop()
