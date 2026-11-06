# Publishing Agent Skills

[![skills.sh](https://skills.sh/b/yangben2019/publishing-agent-skills)](https://skills.sh/yangben2019/publishing-agent-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Turn a folder of `SKILL.md` files into a repository strangers can install with one command.**

A Claude Code skill that encodes the whole release path: the layouts the `npx skills` CLI actually searches, the frontmatter rules that decide whether a skill ever triggers, validation before pushing, licensing for reused code, topics, badges — and an honest account of how skills.sh indexing behaves.

---

## What it covers

| Stage | Detail |
|---|---|
| **Shape** | One skill vs. many, when to split into separate repos |
| **Layout** | The six containers the CLI searches, three levels deep |
| **Frontmatter** | `name` rules, description length and trigger phrasing |
| **Validation** | Bundled `scripts/validate.py` — layout, frontmatter, manifests, README, LICENSE, duplicate names |
| **Testing** | Driving a subagent through a realistic task before publishing |
| **Packaging** | README structure, MIT vs. Apache-2.0 attribution, `.gitignore` for data-heavy repos |
| **Push** | `gh repo create --source=. --push`, and what to do when the CLI times out behind a proxy |
| **Discovery** | Topics that directories actually scan for |
| **Badges** | `skills.sh/b/owner/repo` and what `resource not found` really means |
| **Reality check** | Installing works immediately; indexing does not, and reinstalling your own repo does not force it |

### 中文简介

把一个技能目录变成可以被 `npx skills add` 直接安装的 GitHub 仓库。覆盖目录结构、frontmatter 规则、发布前校验、许可证、topics、徽章，以及 skills.sh 索引的真实行为（安装能立刻用，索引要等）。

---

## Install

```bash
npx skills add yangben2019/publishing-agent-skills
```

Or as a plugin:

```text
/plugin marketplace add yangben2019/publishing-agent-skills
/plugin install publishing-agent-skills@publishing-agent-skills
```

---

## Usage

```text
我把三个技能写好了，帮我按规范打包成 GitHub 仓库并发布。
```

```text
Review my skill repo before I publish it — will the CLI find all the SKILL.md files?
```

```text
我的徽章一直显示 resource not found，是哪里写错了吗？
```

---

## The validator

```bash
python scripts/validate.py /path/to/repo
```

Checks frontmatter, name format and folder match, description length and shape, body size, manifest JSON, README and LICENSE, and duplicate skill names. Exit code 0 means no errors.

It validates structure, not usefulness — a skill can pass and still be unhelpful. That is what the subagent test is for.

---

## Two things this skill will tell you honestly

1. **`npx skills add` works the moment you push.** It clones from GitHub; it does not depend on any directory.
2. **Badges and rankings do not.** A new repo commonly shows `resource not found` for hours or days. Repeatedly installing your own repository does not reliably change that — the index appears to update on its own schedule.

---

## License

MIT © 2026 yangben2019
