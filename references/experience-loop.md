# 从真实纠错更新 Skill

本文件负责跨 Skill 的经验准入、去重和改版流程。工作区的 `maintenance/skill-learnings.json` 保存事件索引及证据路径；作品文件保存完整现场。`quality-samples.json` 保存内容和视觉样例，选题数据回填保存内容表现，这两类记录都不能直接成为 Skill 规则。

## 何时启动

当前任务出现明确用户纠错、实际失败后的人工恢复、重复发生的卡点，或现有规则/模板冲突时，在修好当前产物后检查本次实际激活的 Skill。发布前的制作纠错也适用。普通表达偏好、单次标题/素材选择和没有现场证据的猜测留在作品；不为每次正常执行建经验条目。实际发布结束仍做一次复盘，无可复用发现可在作品内记“无需修改”。

## 一条经验的最小证据

在工作区登记前，先确定：事件 ID、作品或任务 ID、发生阶段与 `production_mode`（适用时）、当前激活的 Skill 和版本、用户反馈或失败现场来源、出错前的实际产物或操作、观察到的结果、修复动作、修复后的结果、适用条件和例外。把观察与原因假设分开写；无法复现的原因标为假设。素材、时间线、页面状态或版本号能定位时写到作品记录，索引只引用该记录。没有可核对的现场或反馈来源时不提升为通用规则。

`maintenance/skill-learnings.json` 使用 `candidate`、`adopted`、`deferred`、`rejected`、`superseded` 状态。`candidate` 仅表示待判断；`adopted` 必须指向已修改或已存在的权威规则及验证结果。直接用户纠错加可核验前后状态，可支持范围明确的单例修正；推测性原因、主观偏好或平台偶发失败，先留 `candidate`，等第二例或针对性复现。数量不是唯一门槛，证据质量和修改风险共同决定。

索引一条记录至少包含 `id`、`work_id`、`owner_skill`、`active_revision`、`stage`、`scope`、`condition`、`action`、`observation`、`recovery`、`outcome`、`feedback_source`、`confidence`、`status`、`evidence` 和 `related_ids`。版本无法查明时明确写 `unknown` 并保留候选；适用制作模式写 `production_mode`。采纳条目还需 `rule_ref` 和 `validation`，其中可写明未做的最终验收。路径相对工作区或 Workbase 维护源，不写凭据或私有素材内容。

## 去重、冲突与所有者

1. 把候选写成“适用条件 → 必须/禁止的动作 → 可观察结果”，搜索同一 Skill、相关消费者、工作区规则和已有经验条目。工作区的 `python3 scripts/skill_learning.py check` 只检查结构、路径和完全相同的归一化条件/动作；相近语义仍需人工查找。
2. 同一条件与动作的后续事件追加为原条目的证据，不复制一条规则。相同动作但媒介、平台或制作模式不同，先确认是否真能共用；保留明确的例外。出现相反动作时核对时间、用户最新选择、现场版本和适用范围；在范围未明确前不要覆盖旧规则。
3. 规则写到拥有该行为的 Skill：选题决策归 `moonlit-topic-engine`，跨形态内容判断归 `moonlit-content-engine/references/editorial-contract.md`，视频口播与 CTA 文案归 `moonlit-video-script`，素材增益/时间线归相应制作 Skill，平台页面恢复归相应发布 Skill。消费者只保留调用或检查提示，链接到所有者。事件索引不能代替可执行规则。
4. 将采纳规则合并到拥有该行为的既有步骤及对应模板/验收；沿入口实际阅读路径检查首次执行能触达，不能只追加补充流程、经验日志或选读文件。把过期的活动模板和相矛盾的入口文字一起更新；历史证据保留，旧规则可标 `superseded` 并指向新条目。一次性的用户选择留在当前作品或配置，不能写成所有作品默认值。

## 改版与验证

先确认当前工程激活快照与 Workbase 维护源的差异，保留双方已有编辑。在维护源做最小修改；有脚本变更时做针对性运行验证，有行为规则变更时用触发案例和一个相邻反例检查适用边界。分别记录静态检查、作者自测、真实现场和用户认可，不混称“验证通过”。之后只对实际修改且已验证的 Skill 执行工程 `skills-pin --skill`，核对锁、链接和 `skills-check`。失败时按工程 `maintenance/WORKFLOW.md` 的 `skills-restore` 回退；不要直接编辑哈希快照。

## 本次示例：真人片尾 CTA

`W-20260927-002` 的 ChatCut 片尾曾把用户已确认的 CTA 素材原声设为 -60 dB；作品记录显示恢复到 0 dB，原录音和音效保留，尚未导出或完成全片听审。`moonlit-talking-head-video` 已有“默认保留原声和音效，不因转写差异静音”的规则，所以登记为现有规则覆盖的一个证据，不再添加同义禁令。`moonlit-video-script` 管 CTA 文案与素材要求；公众号 GIF 静音规则只适用于文章动图，不与真人视频原声规则冲突。

## 方法依据

- [Anthropic Agent Skills 工程说明](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)：从代表性任务中的实际困难迭代 Skill，按需拆分参考文件。
- [OpenAI Agent 评估指南](https://developers.openai.com/api/docs/guides/agent-evals)：先看执行轨迹定位问题，再把明确的案例加入可重复评估。
- [LangSmith 评估类型](https://docs.langchain.com/langsmith/evaluation-types)：真实运行中的失败可进入离线案例集，回归时比较改进与退步。
- [GitHub 重复问题标记](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/marking-issues-or-pull-requests-as-a-duplicate)：相关事件互相链接，保留来源而减少重复维护。

Moonlit 的条目结构、准入门槛和归属规则是针对本工程的设计，不是上述资料的原样规范。
