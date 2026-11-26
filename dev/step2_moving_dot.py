# ============================================
# 步骤 2：让圆点动起来（游戏主循环）
# 目标：理解「擦掉 -> 更新 -> 重画 -> 再预约」四步循环
# ============================================
import tkinter as tk

# 创建窗口
root = tk.Tk()
root.title("会动的小圆点")

# 创建画布：480 宽、640 高、深色背景
canvas = tk.Canvas(root, width=480, height=640, bg="#000011", highlightthickness=0)
canvas.pack()

# 圆点的初始位置（存成变量，位置才能"变"）
x = 240
y = 320

def game_loop():
    global x                          # 告诉函数：我要改的是外面那个 x
    canvas.delete("all")              # ① 擦掉画面（不擦会留下残影，连成一条线）
    x += 2                            # ② 更新位置：每次往右移 2 像素
    # ③ 重新画圆：create_oval(左上x, 上y, 右下x, 下y, fill=颜色)
    canvas.create_oval(x-10, y-10, x+10, y+10, fill="red")
    root.after(16, game_loop)         # ④ 16 毫秒后再调用自己一次（形成循环）

# 启动循环
game_loop()

# 让窗口一直显示（进入主循环）
root.mainloop()
