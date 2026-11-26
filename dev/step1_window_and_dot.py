# ============================================
# 步骤 1：让窗口亮起来，正中间画一个红色圆点
# 目标：理解 tkinter 的窗口、画布、画圆、主循环
# ============================================
import tkinter as tk

# 1. 创建窗口
root = tk.Tk()

# 2. 给窗口起标题
root.title("我的第一个STG")

# 3. 创建画布：480 宽、640 高、深色背景（#000011）
#    highlightthickness=0 表示画布不要外边框
canvas = tk.Canvas(root, width=480, height=640,
                   bg="#000011", highlightthickness=0)

# 4. 把画布放进窗口
canvas.pack()

# 5. 画一个圆：create_oval(左上x, 上y, 右下x, 下y)
#    圆心 (240, 320)，半径 10
#    左上角 = (240-10, 320-10) = (230, 310)
#    右下角 = (240+10, 320+10) = (250, 330)
canvas.create_oval(230, 310, 250, 330, fill="red")

# 6. 让窗口一直显示（进入主循环，直到用户点关闭）
root.mainloop()
