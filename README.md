# 东方 STG 弹幕游戏（期中答辩项目）

## 文件夹说明

- `dev/`：**开发工程文件** —— 每一步一个独立文件，从易到难逐步搭建
- `final/`：**最终展示文件** —— 答辩要交的成品代码、说明文档等

> ⚠️ **重要约定**：每个步骤一个独立文件，后面的文件 = 前面的文件 + 本步新增内容。
> **旧文件不要再改**，它们是快照；要改就在当前最新的文件上改。这样出错可以随时回到上一步。

## 开发进度（打勾 = 已完成）

- [x] 步骤 1：窗口 + 画布 + 画一个圆点（`dev/step1_window_and_dot.py`）
- [x] 步骤 2：让圆点动起来（游戏主循环）（`dev/step2_moving_dot.py`）
- [x] 步骤 3：用 WASD 控制移动（按键集合 + 边界）（`dev/step3_wasd_move.py`）
- [x] 步骤 4：把圆点重构成 Player 类（`dev/step4_player_class.py`）
- [x] 步骤 5：抽象基类 Entity + 继承（`dev/step5_entity_abstract.py`）
- [x] 步骤 6：Bullet 类 + Game 类 + 射击（`dev/step6_bullet_class.py`）
- [x] 步骤 7：Boss + 血条（`dev/step7_boss_class.py`）
- [x] 步骤 8：子弹打中 Boss 掉血（碰撞检测）（`dev/step8_collision.py`）
- [ ] 步骤 9：Boss 弹幕 + 符卡
- [ ] 步骤 10：判定点 / 死亡 / Bomb / 擦弹 / 结算

## 最终展示（final/）

- 东方STG游戏_基础版.py —— 已实现核心玩法（移动/射击/5种弹幕/判定点/胜负结算）
