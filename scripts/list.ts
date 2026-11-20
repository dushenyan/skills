#!/usr/bin/env tsx
/**
 * 终端里一眼扫完的技能清单：每个技能一行「名称 + 一句话用途」。
 * 短描述仅用于终端展示；完整触发规则仍来自各 SKILL.md 的 description（--verbose）。
 *
 * 用法：
 *   skill                       列出全部技能（简短）
 *   skill --verbose             查看完整触发/边界描述
 *   skill --skill=clarify       只看指定技能
 *   skill --search=面试          按名称或描述搜索
 *   skill --source=own          只看自维护 / external 技能
 *   skill --json                JSON 输出
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const skillRoots = [
  { name: 'own', label: '自维护', path: join(repoRoot, 'own') },
  { name: 'external', label: '外部', path: join(repoRoot, 'external') },
]

/** 终端速览用的一句话用途；完整触发规则见各 SKILL.md 的 description。 */
const SHORT_DESCRIPTIONS: Record<string, string> = {
  'arrange-docs': '整理零散初稿为正式文档',
  'article-readability-rewriter': '改写干巴文章，提升阅读兴趣',
  'clarify': '笼统需求先问清再开工',
  'humanizer-zh': '中文去 AI 味，保留原意',
  'image-prompt-designer': '生成配图、封面、信息图提示词',
  'inspect-resume': '简历审查与求职全链路诊断',
  'interactive-concept-visual': '做可动手的单页概念讲解',
  'interview-simulator': '连续多轮技术模拟面试',
  'makefile-style': '统一 Makefile 分类与 help',
  'picgo-upload': '本地图片传图床拿链接',
  'project-highlights-extractor': '项目素材转简历亮点',
  'python-project-spec': 'Python 项目脚手架与规范',
  'ruanyf-answer-style': '阮一峰风格写备考答案',
  'ruanyf-document-style-guide': '中文技术文档排版与行文规范',
  'ruanyf-paper-explainer': '论文、长文变中文解读',
  'script-cli': '现代 CLI 开发最佳实践',
  'shenyan': '个人 JS/TS 项目约定',
  'skill-creator': '从零创建或改进 Agent Skill',
  'skill-polisher': '技能文件体检与打磨',
  'socratic': '追问式思考伙伴',
  'tech-tutorial': '生成系统的中文技术教程',
}

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---/
const INDENTED_LINE_RE = /^\s/
const SPACES_RE = /\s+/g
const SENTENCE_END_RE = /[。！？]/
const TRAILING_PUNCT_RE = /[；。]$/
const LINE_BREAK_RE = /\r?\n/
const SENTENCE_BOUNDARY_RE = /(?<=[。！？；])/
const WHITESPACE_GROUP_RE = /(\s+)/
const STARTS_WITH_PUNCT_RE = /^[，、：,]/
const ENDS_WITH_PUNCT_RE = /[。！？；,]$/
const WHITESPACE_ONLY_RE = /^\s+$/

interface Options {
  help: boolean
  verbose: boolean
  json: boolean
  sources: string[]
  skills: string[]
  search: string[]
}

interface SkillInfo {
  name: string
  /** 终端速览的一句话用途。 */
  short: string
  /** description 第一句。 */
  summary: string
  /** 触发条件、边界等其余内容。 */
  detail: string
  description: string
  source: 'own' | 'external'
  path: string
}

/** 解析 SKILL.md 顶部 frontmatter，只取 description 字段。 */
function readDescription(filePath: string): string | null {
  const content = readFileSync(filePath, 'utf8')
  const match = FRONTMATTER_RE.exec(content)
  if (!match)
    return null

  const lines = match[1].split(LINE_BREAK_RE)
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (!line.startsWith('description'))
      continue
    const afterName = line.slice('description'.length)
    if (!afterName.startsWith(':'))
      continue
    const value = afterName.slice(1).trim()

    if (value === '|' || value === '>') {
      const parts: string[] = []
      for (let j = i + 1; j < lines.length; j++) {
        if (lines[j].trim() && !INDENTED_LINE_RE.test(lines[j]))
          break
        parts.push(lines[j].trim())
      }
      return parts.filter(Boolean).join(value === '|' ? '\n' : ' ').trim()
    }
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith('\'') && value.endsWith('\'')))
      return value.slice(1, -1)
    return value
  }
  return null
}

/** 拆出第一句作为摘要，其余作为触发/边界详情。 */
function splitDescription(description: string): { summary: string, detail: string } {
  const flat = description.replace(SPACES_RE, ' ').trim()
  let end = -1
  for (let i = 2; i < flat.length; i++) {
    if (SENTENCE_END_RE.test(flat[i])) {
      end = i
      break
    }
  }
  if (end >= 0)
    return { summary: flat.slice(0, end + 1), detail: flat.slice(end + 1).trim() }
  const parts = flat.split('；')
  return { summary: parts[0].replace(TRAILING_PUNCT_RE, ''), detail: parts.slice(1).join('；') }
}

function listSkills(): SkillInfo[] {
  const skills: SkillInfo[] = []
  for (const root of skillRoots) {
    for (const entry of readdirSync(root.path, { withFileTypes: true })) {
      if (!entry.isDirectory() || !existsSync(join(root.path, entry.name, 'SKILL.md')))
        continue
      const skillPath = join(root.path, entry.name, 'SKILL.md')
      const description = readDescription(skillPath) ?? '（SKILL.md 未提供 description）'
      const { summary, detail } = splitDescription(description)
      skills.push({
        name: entry.name,
        short: SHORT_DESCRIPTIONS[entry.name] ?? summary.slice(0, 18),
        summary,
        detail,
        description,
        source: root.name as SkillInfo['source'],
        path: relative(repoRoot, skillPath),
      })
    }
  }
  return skills
}

/** 折行：优先在句末标点后换行；超长句按空格/词边界断，英文术语不拆开。 */
function wrap(text: string, width: number): string[] {
  const lines: string[] = []
  const sentences = text.split(SENTENCE_BOUNDARY_RE).map(part => part.trimStart()).filter(Boolean)
  let current = ''

  const flush = () => {
    if (current) {
      lines.push(current)
      current = ''
    }
  }
  const isBreakpoint = (word: string) => STARTS_WITH_PUNCT_RE.test(word) || ENDS_WITH_PUNCT_RE.test(word)

  for (const sentence of sentences) {
    const words = sentence.split(WHITESPACE_GROUP_RE).filter(Boolean)
    const candidate = current + sentence
    if ([...candidate].length <= width) {
      current = candidate
      continue
    }
    for (const word of words) {
      const next = current + word
      if ([...next].length <= width || !current || WHITESPACE_ONLY_RE.test(word)) {
        current = next
        continue
      }
      if (isBreakpoint(word)) {
        lines.push(current.trimEnd())
        current = word.trimStart()
      }
      else {
        flush()
        current = word.trimStart()
      }
    }
  }
  flush()
  return lines.length > 0 ? lines : ['']
}

function splitList(value: string): string[] {
  return value.split(',').map(item => item.trim()).filter(Boolean)
}

function parseArgs(argv: string[]): Options {
  const options: Options = { help: false, verbose: false, json: false, sources: [], skills: [], search: [] }
  for (const arg of argv) {
    if (arg === '-h' || arg === '--help')
      options.help = true
    else if (arg === '-v' || arg === '--verbose')
      options.verbose = true
    else if (arg === '--json')
      options.json = true
    else if (arg.startsWith('--source='))
      options.sources.push(...splitList(arg.slice('--source='.length)))
    else if (arg.startsWith('--skill='))
      options.skills.push(...splitList(arg.slice('--skill='.length)))
    else if (arg.startsWith('--search='))
      options.search.push(...splitList(arg.slice('--search='.length)))
    else
      throw new Error(`未知参数: ${arg}`)
  }
  const unknownSources = options.sources.filter(source => source !== 'own' && source !== 'external')
  if (unknownSources.length > 0)
    throw new Error(`未知来源: ${unknownSources.join(', ')}（可选: own, external）`)
  return options
}

function printHelp(): void {
  console.log(`用法：skill [选项]

列出仓库中的技能。默认每技能一行，只看名称和一句话用途。

选项：
  -v, --verbose    显示完整触发条件与边界说明
  --skill=<names>  只看指定技能，逗号分隔
  --search=<text>  按名称或描述搜索，逗号分隔多个关键词
  --source=<name>  只看 own（自维护）或 external（外部）
  --json           JSON 输出
  --help, -h       显示本帮助

示例：
  skill
  skill --verbose --skill=clarify
  skill --search=面试,简历`)
}

/** 默认视图：按来源分组，两列对齐，一屏扫完。 */
function printCompact(skills: SkillInfo[]): void {
  if (skills.length === 0) {
    console.log('没有匹配的技能。')
    return
  }
  const width = Math.max(...skills.map(skill => [...skill.name].length)) + 2
  let group = ''
  for (const skill of skills) {
    const label = skillRoots.find(root => root.name === skill.source)?.label ?? skill.source
    if (label !== group) {
      group = label
      console.log(`\n${label}（${skills.filter(item => item.source === skill.source).length}）`)
    }
    console.log(`  ${skill.name.padEnd(width)}${skill.short}`)
  }
  console.log(`\n共 ${skills.length} 个技能。用 skill --verbose 看完整触发条件。\n`)
}

/** 详细视图：每个技能名称 + 完整描述折行。 */
function printVerbose(skills: SkillInfo[]): void {
  if (skills.length === 0) {
    console.log('没有匹配的技能。')
    return
  }
  console.log(`共 ${skills.length} 个技能：\n`)
  for (const skill of skills) {
    const label = skillRoots.find(root => root.name === skill.source)?.label ?? skill.source
    console.log(`${skill.name}（${label}）`)
    for (const line of wrap(skill.summary, 110))
      console.log(`  ${line}`)
    if (skill.detail) {
      for (const line of wrap(skill.detail, 106))
        console.log(`    ${line}`)
    }
    console.log('')
  }
}

process.stdout.on('error', (error: NodeJS.ErrnoException) => {
  if (error.code === 'EPIPE')
    process.exit(0)
  throw error
})

try {
  const options = parseArgs(process.argv.slice(2))
  if (options.help) {
    printHelp()
  }
  else {
    let skills = listSkills()
    if (options.sources.length > 0)
      skills = skills.filter(skill => options.sources.includes(skill.source))
    if (options.skills.length > 0)
      skills = skills.filter(skill => options.skills.includes(skill.name))
    if (options.search.length > 0) {
      const keywords = options.search.map(keyword => keyword.toLocaleLowerCase())
      skills = skills.filter(skill => keywords.some(keyword =>
        skill.name.toLocaleLowerCase().includes(keyword)
        || skill.short.toLocaleLowerCase().includes(keyword)
        || skill.description.toLocaleLowerCase().includes(keyword),
      ))
    }
    // 按来源分组展示，组内按名称排序；速览视图不再出现分组标题反复横跳。
    skills.sort((a, b) => {
      const sourceDiff = skillRoots.findIndex(root => root.name === a.source) - skillRoots.findIndex(root => root.name === b.source)
      return sourceDiff !== 0 ? sourceDiff : a.name.localeCompare(b.name, 'zh-CN')
    })

    if (options.json)
      console.log(JSON.stringify(skills, null, 2))
    else if (options.verbose)
      printVerbose(skills)
    else
      printCompact(skills)
  }
}
catch (error) {
  console.error(`✗ ${error instanceof Error ? error.message : String(error)}`)
  process.exit(1)
}
