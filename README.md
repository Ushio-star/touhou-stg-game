# 东方 STG 弹幕游戏（OOP 课程答辩项目）

基于 **Python 3 + Tkinter** 标准库实现的东方 Project 风格 Boss 战弹幕游戏。

## 项目目标

- 抽象基类 `Entity`（`update()` / `draw()`），玩家、Boss、子弹均继承自它
- `Game` 类统一管理主循环：清屏 → 统一 `update()` → 统一 `draw()`，用 `root.after()` 维持约 60 FPS
- 真实判定点（视觉模型与受击判定分离）
- 符卡系统、多种弹幕类型、决死 Bomb、擦弹计分、结算界面

## 运行

```bash
python main.py
```

## 开发进度

- [ ] 项目骨架（Entity / Game 主循环）
- [ ] 玩家系统（移动 / 射击 / 低速 / 判定点）
- [ ] Boss 与符卡系统
- [ ] 弹幕类型（自机子弹 / 分裂 / 大玉 / 高密度演出）
- [ ] 结算与额外机制（Bomb / 擦弹 / 掉落）
