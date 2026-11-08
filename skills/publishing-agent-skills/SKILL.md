---
name: publishing-agent-skills
description: Package agent skills into a public GitHub repository that people can install with npx skills add — the accepted repo layouts, frontmatter rules, validation, licensing, topics, README and badges, plus an honest account of how skills.sh indexing actually behaves. Use when the user wants to publish skills, create a plugin marketplace repo, add a skills.sh badge, or asks why their skill repo is not installable or not showing up in a directory.
---

# Publishing agent skills

Turn a folder of `SKILL.md` files into a repository strangers can install in one command. Most of the work is layout and validation; the publishing step is short, and the indexing step is the one nobody warns you about.

## Language

Reply in the language the user wrote in. Repository names, skill names, frontmatter fields, commands and file paths stay in English. Translate headings and prose, never identifiers. When you draft a README or a description for the user, ask which language it should be in — a published README is read by strangers, not by the author.

## 中文说明

把一个技能目录变成能被 `npx skills add` 安装的 GitHub 仓库。

1. **布局**：`skills/<name>/SKILL.md`，或在 `.claude-plugin` 里声明路径
2. **frontmatter**：`name` 小写连字符且与文件夹同名；`description` 写清"做什么 + 何时用"
3. **校验**：`python scripts/validate.py <仓库>`
4. **测试**：让子代理按技能跑一个真实任务，而不是只看结构
5. **发布**：`gh repo create --public --source=. --push`
6. **要点**：安装立刻可用；徽章和排行榜依赖 skills.sh 自己的索引，重复安装自己仓库并不会催它

## 1. Decide the shape

| Situation | Shape |
|---|---|
| One skill | Repo with a single `skills/<name>/SKILL.md` |
| Several related skills | One repo, one `skills/` folder, one plugin manifest |
| Several unrelated skills | Separate repos — one repo with unrelated skills has no coherent description and triggers badly |

Repo name and skill name should both be literal and searchable: `graphhopper-routing`, not `PathWizard`.

## 2. Layout that the CLI actually finds

`npx skills add owner/repo` searches these, up to three levels deep:

```
SKILL.md                          # repo root
skills/<name>/SKILL.md            # flat — the common case
skills/<category>/<name>/SKILL.md
skills/<category>/<category>/<name>/SKILL.md
.claude/skills/<name>/SKILL.md
.agents/skills/<name>/SKILL.md
```

It also honours skill paths declared in `.claude-plugin/marketplace.json` or `plugin.json`. A repo can contain several skills; a shallower `SKILL.md` wins over a deeper one.

**Do not** put a second `SKILL.md` at the repo root when you already use `skills/`. The CLI may treat it as a second skill.

Minimal publishable plugin:

```
repo/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/<skill-name>/SKILL.md
├── README.md
├── LICENSE
└── .gitignore
```

```json
// marketplace.json
{
  "name": "<marketplace-name>",
  "owner": { "name": "<github-user>" },
  "plugins": [
    { "name": "<plugin-name>", "source": "./", "description": "<one line>" }
  ]
}
```

`source: "./"` lets the CLI scan `skills/` itself. Listing paths explicitly is more brittle.

## 3. Frontmatter rules

```yaml
---
name: lowercase-kebab-case
description: What it does. Use when <specific triggers>.
---
```

- `name`: lowercase letters, digits, hyphens; ≤ 64 chars; must match the folder name; must not contain `anthropic` or `claude`.
- `description`: ≤ 1024 chars, third person, and it must say **both** what the skill does and when to use it. This is the only thing the model sees before deciding to load the skill — a vague description silently kills the skill.
- Put trigger phrases in the description, including the words a real user would type. For bilingual audiences, include both languages.
- No "when to use" section in the body — it belongs in the description.

## 4. Validate before you push

Run the bundled validator:

```bash
python scripts/validate.py <path-to-repo>
```

It checks: frontmatter present and closed, name format and folder match, description length and shape, body size, manifest JSON validity, presence of README and LICENSE, and duplicate names across repos.

Fix errors before publishing. A repo that fails validation usually still installs — but it triggers badly, which is worse than not existing.

## 5. Test behaviour, not just structure

Structure checks prove the skill loads. They do not prove it helps.

Spawn a subagent with the skill path and a realistic task:

```
Read the skill at <path>/SKILL.md and follow it exactly to complete:
<realistic user request>
Return only the final answer, in the user's language.
```

Read the output. If it ignores the skill's workflow or invents facts, the body needs work — not the description.

## 6. Package the repo

**README** should contain, in this order: badge, one-line pitch, skill table, install commands for all three routes, 3–4 real usage examples, and a short "what it is / is not".

**LICENSE**: MIT is the default. If you copy Apache-2.0 code from another project, keep the license text and add a `THIRD_PARTY.md` naming the origin and what was reused.

**.gitignore**: at minimum exclude data files and build output. For GIS or routing repos, explicitly ignore `*.osm.pbf` and `graph-cache*/` — committing those is unrecoverable history bloat.

## 7. Push

```bash
git init -b main
git add .
git commit -m "feat: <what the skill does>"
gh repo create <name> --public --source=. --push --description "<one line>"
```

If `gh` reports a network timeout but `Test-NetConnection github.com -Port 443` succeeds, the machine likely needs an explicit proxy:

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7897"
$env:HTTP_PROXY="http://127.0.0.1:7897"
```

If the user has not authenticated: `gh auth login --hostname github.com --git-protocol https --web`.

## 8. Topics

Topics drive discovery far more than the description does. Use 10–18, all lowercase, mixing broad and specific:

```bash
gh repo edit owner/repo \
  --add-topic claude-code --add-topic claude-plugin --add-topic agent-skills \
  --add-topic <domain-topic> --add-topic <specific-topic>
```

Always include `claude-code`, `claude-plugin`, `agent-skills` — directories scan for them.

## 9. Badge

```markdown
[![skills.sh](https://skills.sh/b/OWNER/REPO)](https://skills.sh/OWNER/REPO)
```

`/b/` returns an SVG (the badge); without `/b/` you get the HTML page. The badge is generated server-side from skills.sh's index — it is not a file in the repo.

## 10. What indexing actually does

This is where expectations go wrong.

- **Install-like-anything works immediately.** `npx skills add owner/repo` clones straight from GitHub; it does not depend on skills.sh.
- **The badge and leaderboard depend on skills.sh's own index**, which is not updated at push time.
- A brand-new repo commonly returns `custom badge / resource not found` for hours to days.
- The FAQ says installs are tracked through anonymous telemetry — but **repeatedly installing your own repo does not reliably force indexing**. In practice a repo sometimes resolves well after publishing with no known trigger, which is consistent with periodic crawling.

Tell the user this plainly instead of promising the badge will appear. If it has not resolved after several days, open an issue on `vercel-labs/skills` **requesting indexing** — that is a feature request, not a bug report about the user's skill.

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `npx skills add` finds 0 skills | `SKILL.md` deeper than three levels, or not under a recognised container | Move to `skills/<name>/SKILL.md` |
| Repo installs but skill never triggers | Description lacks trigger phrases | Rewrite the description; rerun the trigger check |
| Two skills appear from one repo | A stray root-level `SKILL.md` plus `skills/` | Delete the root one |
| `gh` times out but network is up | Proxy not applied to the CLI | Set `HTTPS_PROXY` for the shell |
| Badge says `resource not found` | Not indexed yet | Wait, or request indexing |
| Push rejected for size | Committed data files | Add them to `.gitignore`, rewrite history or re-init |

## 12. Release checklist

- [ ] Layout is `skills/<name>/SKILL.md`
- [ ] `name` matches the folder and is lowercase kebab
- [ ] Description states both *what* and *when*, with real trigger phrases
- [ ] `python scripts/validate.py <repo>` passes with no errors
- [ ] A subagent completed a realistic task using the skill
- [ ] README has badge, install commands and examples
- [ ] LICENSE present; `THIRD_PARTY.md` if any upstream code was reused
- [ ] `.gitignore` excludes data and build output
- [ ] 10+ topics added
- [ ] `npx skills add owner/repo` verified from a clean temp directory
