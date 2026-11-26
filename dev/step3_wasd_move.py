# ============================================
# 步骤 3：用 WASD / 方向键移动圆点（按键集合）
# 目标：理解"用集合记录按键状态"实现平滑移动
# ============================================
import tkinter as tk

# 创建窗口和画布
root = tk.Tk()
root.title("用 WASD 移动圆点")
canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
canvas.pack()

# 圆点位置和移动速度
x = 240
y = 320
SPEED = 4

# 用一个集合记录"当前正按着的键"
keys = set()

def on_press(event):
    keys.add(event.keysym)      # 按下：把键名装进集合

def on_release(event):
    keys.discard(event.keysym)  # 松开：把键名从集合拿出

# 绑定按键按下/松开事件
root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)

def game_loop():
    global x, y
    canvas.delete("all")                     # ① 擦掉画面

    # ② 根据按着的键移动（按住就一直动 = 平滑移动）
    if "Left" in keys or "a" in keys:  x -= SPEED   # 左
    if "Right" in keys or "d" in keys: x += SPEED   # 右
    if "Up" in keys or "w" in keys:    y -= SPEED   # 上
    if "Down" in keys or "s" in keys:  y += SPEED   # 下

    x = max(10, x)
    x = min(470, x)
    y = max(10, y)
    y = min(630, y)
    
    # ③ 重新画圆
    canvas.create_oval(x-10, y-10, x+10, y+10, fill="red")
    root.after(16, game_loop)                # ④ 16 毫秒后再来

# 启动循环
game_loop()
root.mainloop()
