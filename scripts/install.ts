#!/usr/bin/env tsx
/**
 * 一键把本仓库 `own/` 与 `external/` 下的技能安装到本地 AI 编辑器的全局技能目录。
 *
 * 用法：
 *   pnpm skills                            全量对齐：所有技能装到所有已检测到的编辑器（软链接）
 *   pnpm skills --copy                     用文件复制代替软链接
 *   pnpm skills --target=claude,workbuddy  只安装到指定编辑器
 *   pnpm skills --skill=cli,resume         只安装指定技能
 *   pnpm skills --uninstall                从各编辑器移除本仓库的技能
 *   pnpm skills --dry-run                  只打印将要执行的操作，不落盘
 *
 * 说明：
 * - 编辑器通过其配置目录（如 `~/.claude`）是否存在来自动检测。
 * - 默认使用软链接，仓库里的技能改动会即时生效；`--copy` 则复制一份。
 * - 仓库里 own/（自维护）与 external/（外部引入）并列，安装时统一平铺到编辑器的 skills/ 目录；
 *   技能目录名即安装名，两处不得重名，否则会互相覆盖。
 * - 不带 `--skill` / `--target` 时执行全量对齐：仓库里的每个技能都会装到每个已检测到的
 *   编辑器，编辑器里指向本仓库但已从仓库删除的残留会被清理，保证各编辑器的技能集合一致。
 * - 只会操作本仓库装出去的技能：指向仓库的软链接、内容一致的副本。编辑器里的同名技能
 *   会被跳过并给出提示，需要 `--force` 才会覆盖或移除；其他技能更不会碰到。
 */

import { cpSync, existsSync, lstatSync, mkdirSync, readdirSync, readFileSync, readlinkSync, rmSync, symlinkSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join, resolve, sep } from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
// own/ 存自维护技能，external/ 存外部引入技能。安装时两者平铺到同一个 skills/ 目录，
// 因此必须分开记录源路径，安装目标仍只用技能名。
const skillRoots = [join(repoRoot, 'own'), join(repoRoot, 'external')]
// 目录重组前的旧根目录。仅用于识别「已装出去的软链接属于本仓库」，让全量对齐能就地更新。
// 不作为扫描源，等所有编辑器都跑过一次全量对齐后可移除。
const legacySkillRoot = join(repoRoot, 'skills')
const home = homedir()

interface Editor {
  id: string
  label: string
  configDir: string
  /** 可选别名，`--target` 时按产品名指定更顺手。 */
  aliases?: string[]
}

/**
 * 支持自动检测的编辑器：配置目录存在即视为已安装，技能目录统一为 `<配置目录>/skills`。
 * `configDir` 取自各客户端自己的用户目录名（Electron 应用可从 product.json 的 dataFolderName 查到）。
 * 目录路径以 [vercel-labs/skills](https://github.com/vercel-labs/skills) 的支持列表为准；
 * 需要新增客户端时在此追加一行即可。
 */
const EDITORS: Editor[] = [
  // Anthropic
  { id: 'claude', label: 'Claude Code', configDir: join(home, '.claude') },
  // 厂商无关的共享目录，多个 CLI 共用一套技能
  {
    id: 'agents',
    label: '通用目录（Cline / Zed / Warp / Kimi Code）',
    configDir: join(home, '.agents'),
    aliases: ['universal'],
  },
  { id: 'config-agents', label: '通用目录（Amp / Replit）', configDir: join(home, '.config', 'agents'), aliases: ['amp', 'replit'] },
  // Qoder
  { id: 'qoder', label: 'Qoder', configDir: join(home, '.qoder') },
  { id: 'qoder-cn', label: 'Qoder CN', configDir: join(home, '.qoder-cn') },
  // OpenAI / Google
  { id: 'codex', label: 'Codex', configDir: join(home, '.codex') },
  { id: 'gemini', label: 'Gemini CLI', configDir: join(home, '.gemini') },
  { id: 'antigravity', label: 'Antigravity', configDir: join(home, '.gemini', 'antigravity') },
  // Cursor 系
  { id: 'cursor', label: 'Cursor', configDir: join(home, '.cursor') },
  { id: 'windsurf', label: 'Windsurf', configDir: join(home, '.codeium', 'windsurf') },
  // 其他常见 CLI
  { id: 'copilot', label: 'GitHub Copilot CLI', configDir: join(home, '.copilot') },
  { id: 'opencode', label: 'OpenCode', configDir: join(home, '.config', 'opencode') },
  { id: 'qwen', label: 'Qwen Code', configDir: join(home, '.qwen') },
  { id: 'iflow', label: 'iFlow CLI', configDir: join(home, '.iflow') },
  { id: 'kilo', label: 'Kilo Code', configDir: join(home, '.kilo') },
  { id: 'roo', label: 'Roo Code', configDir: join(home, '.roo') },
  // 国内客户端
  { id: 'codebuddy', label: 'CodeBuddy', configDir: join(home, '.codebuddy') },
  { id: 'codebuddy-cn', label: 'CodeBuddy CN', configDir: join(home, '.codebuddycn') },
  { id: 'trae', label: 'Trae', configDir: join(home, '.trae') },
  // Trae CN 与 TraeWork CN（TRAE SOLO 桌面版）的 dataFolderName 都是 .trae-cn，共用一套技能目录
  {
    id: 'trae-cn',
    label: 'Trae CN / TraeWork CN',
    configDir: join(home, '.trae-cn'),
    aliases: ['traework-cn', 'traework'],
  },
  // VS Code / JetBrains 里的 Trae 插件（原 MarsCode）
  {
    id: 'trae-plugin',
    label: 'Trae 插件（VS Code / JetBrains）',
    configDir: join(home, '.marscode'),
    aliases: ['marscode', 'trae-vscode'],
  },
  { id: 'workbuddy', label: 'WorkBuddy', configDir: join(home, '.workbuddy') },
]

interface Options {
  dryRun: boolean
  copy: boolean
  uninstall: boolean
  force: boolean
  help: boolean
  targets: string[]
  skills: string[]
}

const useColor = Boolean(process.stdout.isTTY) && !process.env.NO_COLOR
const paint = (code: number, text: string) => (useColor ? `\u001B[${code}m${text}\u001B[0m` : text)
const gray = (text: string) => paint(90, text)
const green = (text: string) => paint(32, text)
const yellow = (text: string) => paint(33, text)
const red = (text: string) => paint(31, text)
const bold = (text: string) => paint(1, text)

const logOk = (message: string) => console.log(`  ${green('✓')} ${message}`)
const logSkip = (message: string) => console.log(`  ${gray('·')} ${gray(message)}`)
const logWarn = (message: string) => console.warn(`${yellow('!')} ${message}`)
const logError = (message: string) => console.error(`${red('✗')} ${message}`)

function splitList(value: string): string[] {
  return value.split(',').map(item => item.trim()).filter(Boolean)
}

function parseArgs(argv: string[]): Options {
  const options: Options = { dryRun: false, copy: false, uninstall: false, force: false, help: false, targets: [], skills: [] }

  for (const arg of argv) {
    if (arg === '-n' || arg === '--dry-run')
      options.dryRun = true
    else if (arg === '--copy')
      options.copy = true
    else if (arg === '-f' || arg === '--force')
      options.force = true
    else if (arg === '-u' || arg === '--uninstall')
      options.uninstall = true
    else if (arg === '-h' || arg === '--help')
      options.help = true
    else if (arg.startsWith('--target='))
      options.targets.push(...splitList(arg.slice('--target='.length)))
    else if (arg.startsWith('--skill='))
      options.skills.push(...splitList(arg.slice('--skill='.length)))
    else
      throw new Error(`未知参数: ${arg}`)
  }

  return options
}

function pathExists(path: string): boolean {
  try {
    lstatSync(path)
    return true
  }
  catch {
    return false
  }
}

function isLinkedTo(dest: string, target: string): boolean {
  try {
    if (!lstatSync(dest).isSymbolicLink())
      return false
    return resolve(dirname(dest), readlinkSync(dest)) === target
  }
  catch {
    return false
  }
}

/** 是否是安装脚本留下的软链接（指向本仓库 own/ 或 external/ 下的某个目录）。 */
function pointsIntoRepo(dest: string): boolean {
  try {
    if (!lstatSync(dest).isSymbolicLink())
      return false
    const link = resolve(dirname(dest), readlinkSync(dest))
    return [...skillRoots, legacySkillRoot].some(root => link === root || link.startsWith(`${root}${sep}`))
  }
  catch {
    return false
  }
}

/** `--copy` 装出去的旧副本：内容一致时覆盖是无损的，可以安全替换。 */
function isRepoCopy(dest: string, source: string): boolean {
  try {
    return readFileSync(join(dest, 'SKILL.md')).equals(readFileSync(join(source, 'SKILL.md')))
  }
  catch {
    return false
  }
}

/**
 * 汇总两个源根目录下的技能，返回「安装名 -> 源绝对路径」。
 * 装到编辑器后只用安装名平铺，所以源路径必须在安装时逐个解析，不能假设单一根目录。
 */
function listSkills(): Map<string, string> {
  const found = new Map<string, string>()
  for (const root of skillRoots) {
    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory() || !existsSync(join(root, entry.name, 'SKILL.md')))
        continue
      if (found.has(entry.name))
        throw new Error(`技能重名: ${entry.name}（同时存在于多个源目录，装到编辑器会互相覆盖）`)
      found.set(entry.name, join(root, entry.name))
    }
  }
  return found
}

function pickSkills(all: string[], requested: string[]): string[] {
  const unknown = requested.filter(name => !all.includes(name))
  if (unknown.length > 0)
    throw new Error(`未知技能: ${unknown.join(', ')}（可选: ${all.join(', ')}）`)
  return all.filter(name => requested.includes(name))
}

function pickEditors(targets: string[]): Editor[] {
  if (targets.length === 0)
    return EDITORS.filter(editor => existsSync(editor.configDir))

  const map = new Map<string, Editor>()
  for (const editor of EDITORS) {
    map.set(editor.id, editor)
    for (const alias of editor.aliases ?? [])
      map.set(alias, editor)
  }

  const unknown = targets.filter(id => !map.has(id))
  if (unknown.length > 0)
    throw new Error(`未知编辑器: ${unknown.join(', ')}（可选: ${EDITORS.map(editor => editor.id).join(', ')}）`)

  // 别名可能指向同一个编辑器，去重后同一目录只安装一次
  const picked = new Set(targets.map(id => map.get(id)).filter(Boolean) as Editor[])
  return [...picked]
}

function ensureDir(path: string, dryRun: boolean): void {
  if (existsSync(path) || dryRun)
    return
  mkdirSync(path, { recursive: true })
}

/**
 * 清理编辑器里指向本仓库、但仓库中已不存在的技能（含改名后的旧名）。
 * 只删本仓库软链接，编辑器自带的其他技能原样保留。
 */
function removeOrphans(targetDir: string, keep: string[], dryRun: boolean): void {
  if (!existsSync(targetDir))
    return
  for (const entry of readdirSync(targetDir)) {
    if (keep.includes(entry))
      continue
    const dest = join(targetDir, entry)
    if (!pointsIntoRepo(dest))
      continue
    if (!dryRun)
      rmSync(dest, { recursive: true, force: true })
    logOk(`清理 ${entry}（仓库中已不存在）`)
  }
}

function installSkills(options: Options): void {
  const skillMap = listSkills()
  const allSkills = [...skillMap.keys()].sort()
  if (allSkills.length === 0) {
    logError(`在 ${gray(skillRoots.join(' 与 '))} 下没有找到任何技能（技能目录需包含 SKILL.md）`)
    process.exit(1)
  }

  const skills = options.skills.length > 0 ? pickSkills(allSkills, options.skills) : allSkills
  const editors = pickEditors(options.targets)
  /** 未限定技能范围时才做全量对齐，避免 `--skill` 子集安装误删其他技能。 */
  const fullSync = options.skills.length === 0

  if (editors.length === 0) {
    logWarn('未检测到任何受支持的编辑器，可用 `--target=claude,qoder,codex,gemini,trae-cn,workbuddy` 显式指定')
    return
  }

  if (!options.uninstall && !fullSync)
    logWarn('子集安装：未列出的技能与编辑器保持不变，运行不带参数的 `make skills` 可全量对齐')

  const action = options.uninstall ? '移除' : options.copy ? '复制安装' : '软链接安装'
  const prefix = options.dryRun ? `${yellow('[dry-run]')} ` : ''
  console.log(`${prefix}${bold(action)} ${skills.length} 个技能 → ${editors.length} 个编辑器（${skills.join(', ')}）\n`)

  for (const editor of editors) {
    const targetDir = join(editor.configDir, 'skills')
    if (!options.uninstall)
      ensureDir(targetDir, options.dryRun)

    console.log(`${bold(editor.label)} ${gray(targetDir)}`)

    for (const name of skills) {
      const dest = join(targetDir, name)
      const source = skillMap.get(name)!
      const existed = pathExists(dest)

      // 只动本仓库装出去的东西：指向仓库的软链接、内容一致的副本，或显式 --force
      if (existed && !options.force && !pointsIntoRepo(dest) && !isRepoCopy(dest, source)) {
        logWarn(`跳过 ${name}：${targetDir} 下的同名技能并非本仓库安装，${options.uninstall ? '不移除' : '不覆盖'}（加 --force 可强制）`)
        continue
      }

      if (options.uninstall) {
        if (!existed) {
          logSkip(`跳过 ${name}（未安装）`)
          continue
        }
        if (!options.dryRun)
          rmSync(dest, { recursive: true, force: true })
        logOk(`移除 ${name}`)
        continue
      }

      if (!options.copy && isLinkedTo(dest, source)) {
        logSkip(`跳过 ${name}（软链接已指向仓库）`)
        continue
      }

      if (existed && !options.dryRun)
        rmSync(dest, { recursive: true, force: true })

      if (!options.dryRun) {
        if (options.copy)
          cpSync(source, dest, { recursive: true })
        else
          symlinkSync(source, dest, 'dir')
      }

      logOk(`${existed ? '更新' : '安装'} ${name}${options.copy ? '（复制）' : ''}`)
    }

    if (fullSync)
      removeOrphans(targetDir, options.uninstall ? [] : allSkills, options.dryRun)

    console.log('')
  }

  if (options.dryRun)
    logWarn('dry-run 模式：以上操作未真正执行')
}

function printHelp(): void {
  console.log(`${bold('用法')}：pnpm skills [选项]

默认（不带选项）执行全量对齐：仓库里的所有技能装到所有已检测到的编辑器，
并清理编辑器中指向本仓库、但仓库里已删除的技能，保证各编辑器技能一致。

${bold('选项')}
  --target=<ids>   只安装到指定编辑器，逗号分隔
                   可选: ${EDITORS.map(editor => editor.id).join(', ')}
                   别名: ${EDITORS.flatMap(editor => editor.aliases ?? []).join(', ')}
  --skill=<names>  只安装指定技能，逗号分隔（此时不做残留清理）
  --copy           复制文件而不是创建软链接
  --force, -f      允许覆盖/移除编辑器里的同名技能（默认跳过非本仓库安装的技能）
  --uninstall, -u  从各编辑器移除本仓库的技能
  --dry-run, -n    只打印将要执行的操作
  --help, -h       显示本帮助

${bold('示例')}
  pnpm skills
  pnpm skills --target=claude,qoder
  pnpm skills --target=traework-cn,codex,gemini
  pnpm skills --skill=cli,resume --copy
  pnpm skills --uninstall --target=trae-cn`)
}

try {
  const options = parseArgs(process.argv.slice(2))
  if (options.help)
    printHelp()
  else
    installSkills(options)
}
catch (error) {
  logError(error instanceof Error ? error.message : String(error))
  process.exit(1)
}
