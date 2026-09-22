![Skill 设计师：把可重复的任务，做成可维护的能力](assets/readme/hero.png)

# 月明·Skill 设计师

从真实任务出发，创建、审查或整理可复用 Skill，让职责、依赖和失败恢复更清楚。

## 你会得到什么

- 明确输入、输出和适用边界的 Skill 设计
- 带问题位置与证据的轻量只读审计报告
- 在授权范围内完成的局部整改和验证说明

## 试着这样说

```text
用 moonlit-skill-creator。审查这几个 Skill 的职责和依赖，指出影响独立安装的问题。先给证据和建议，不修改业务流程。
```

## 安装与首次使用

将本仓库的完整目录交给支持本地 Skill 的 Agent 安装，保留 `SKILL.md` 与随附资源。已有同名版本时先检查差异；使用版本锁的工作区沿用自身升级机制。

让 Agent 安装：

```text
请安装这个 Skill：https://github.com/zzyong24/moonlit-skill-creator
```

也可通过 Skills CLI 安装：

```bash
npx skills add zzyong24/moonlit-skill-creator
```

## 配置与依赖

设计与审读无需额外账号。随附本地审计脚本要求 Python 3.10+，只使用标准库。oil-skill-creator 是可选的深入评审工具，不是运行依赖。

## 数据与使用边界

审计脚本读取本地文件，不联网。静态审计不等于秘密扫描、业务效果或跨平台验收。读取外部资料和发布仓库按当前任务范围执行。

## 详细说明

执行流程与资源导航见 [SKILL.md](SKILL.md)。安装检查不代表真实业务验收；需要外部服务、账号登录或付费生成的步骤，应在使用者自己的环境中验证。

---

月明水清深 · `moonlit-skill-creator`

首图为 AI 生成的品牌概念插画，不是工具截图或执行结果。
