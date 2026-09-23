# 独立 Skill 仓库与品牌规范

本规范适用于准备在 GitHub 独立展示或分发的月明 Skill。它统一仓库门面，不改变 Skill 的职责设计，也不要求为每次本地改动发布。

## 名称与权威来源

- 技术名称使用 `moonlit-<capability>`。Skill 目录名、`SKILL.md` frontmatter `name`、GitHub 仓库名、README 安装目录和评估配置中的 `skill_name` 完全一致。
- 面向人的中文名称使用“月明·<能力名称>”。`agents/openai.yaml` 的 `display_name`、README 标题和导航用同一名称；描述准确说清能力，不把旧引擎或弃用流程包装成当前 Skill。
- 所有月明 Skill 的 canonical source 集中在 `moonlit-skills/skills/moonlit-*/`。项目运行快照、用户安装入口和独立 GitHub 仓库都是派生副本，不各自成为第二份维护源。
- 独立仓库只发布一个 Skill。目录结构清楚、能从仓库根目录使用；携带适用的 `SKILL.md`、README、许可证、必要脚本/资源和评估样例。README 中的仓库 URL、相对链接和安装路径必须指向新名称。
- 创建或公开仓库只能在用户明确授权后进行。准备分发可以先完成本地审查和交付文件，不编造远程地址，也不把过往授权理解为未来发布许可。

## README 首图

- 独立 Skill 仓库 README 使用一张横版概念首图：1774 × 887、不透明 PNG，放在 `assets/readme/hero.png`，并置于 README 顶部。
- 全系列统一采用浅色纸面、深色手绘线稿、克制的绿色/月牙品牌元素及月明宇航员品牌形象。以已发布的月明 Skill 首图为风格参考；每张图再按本 Skill 的真实功能设计独立场景。
- 图是 README 品牌首图，不是必须另做的方形 App 图标，也不能伪装成真实软件界面、运行结果或截图。不要使用其他项目的旧配色、随机科技底纹、未经授权的平台标志或装饰性假数据。
- README 在适当位置引用该图。确认 PNG 尺寸、背景、留白和品牌元素；生成图中的中文如果不可靠，避免把关键名称交给图像模型绘制，可在 HTML/Markdown 标题中清晰呈现。
- 不为一个 Skill 制作多套彼此冲突的头像、配色或标题风格。若既有首图不符合统一标准，更新首图和其 README 引用，不继续叠加第二套视觉。

## 发布前检查

逐项核对：

1. Skill 名称、目录、仓库、README 标题、安装命令和评估 `skill_name` 一致。
2. README 首图位于 `assets/readme/hero.png`，尺寸是 1774 × 887 的不透明 PNG，呈现统一品牌视觉和独立功能场景。
3. 首次安装、依赖、运行示例、限制、许可证和本地相对链接有效；不含本机路径、密钥、Cookie、登录态、运行输出或私人资料。
4. `SKILL.md` 的前置元数据和 `agents/openai.yaml` 命名准确，评估用例对应当前 Skill。
5. 从 canonical source 复制/同步后的差异可解释；发布后记录仓库 URL 和提交版本，后续修改仍先回到 canonical source。

品牌图生成或重做时使用 imagegen Skill，提供已发布月明 Skill 首图作为风格参考，并给出独立场景描述。验收视觉结果后再写入正式资产路径；不要因为仓库即将发布而省略图像审看。
