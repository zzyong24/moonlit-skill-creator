# 设计来源与取舍

本 Skill 是独立归纳，不是将外部项目全文复制为模板。

## Oil Skill Creator

- 来源：https://github.com/oil-oil/oil-skill-creator
- 研究版本：`45b0b00720ec2bcd442fe65d91a3ac3e8937934d`，MIT。
- 重点：`SKILL.md`、`references/information-architecture.md`、`product-design.md`、`review-and-remediation.md`、`evaluation.md`、`compatibility.md`、`publishing.md`。
- 采用：首次使用与恢复、渐进披露、审查与整改分开、静态检查与效果评测分开、逐项证据及可分发性。
- 不普遍照搬：固定凭据页面、强制完整 A/B 测试、每次人工停点。只在真实任务和权限需要时应用。

## Hypit

- 来源：https://github.com/hypit-ai/hypit
- 本地研究版本：`f4081f909c0d84e42023ef3d972a9b474bad5efd`。
- 重点：`skills/hypit/SKILL.md`、`skills/hypit/references/production/component-design.md`、`production/system.md`、`creation/project-files.md`、`packages/runtime-kit/README.md`、`docs/guide/studio-companion-architecture.md`。
- 采用：责任/参数/复用分开决策，语义与实现分离，修改回到所有者，执行与产物分离，公共协议、按依赖恢复及项目边界。
- 不照搬：视频时间投影、运行时模型注册、Companion 面板等完整实现。只有相应问题存在时才设计同等级机制。

## 宿主 Skill Creator

结合当前宿主的 Skill 创建规范：少而有效的指导、用户意图优先、窄修优先、可选 UI 元数据、真实行为验证。宿主格式变化时核对当前文档，不把本文当作永久格式标准。
