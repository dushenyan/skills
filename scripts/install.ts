#!/usr/bin/env tsx
/**
 * 一键把本仓库 `skills/` 下的技能安装到本地 AI 编辑器的全局技能目录。
 *
 * 用法：
 *   pnpm skills                            安装全部技能到所有已检测到的编辑器（软链接）
 *   pnpm skills --copy                     用文件复制代替软链接
 *   pnpm skills --target=claude,workbuddy  只安装到指定编辑器
 *   pnpm skills --skill=cli,resume         只安装指定技能
 *   pnpm skills --uninstall                从各编辑器移除本仓库的技能
 *   pnpm skills --dry-run                  只打印将要执行的操作，不落盘
 *
 * 说明：
 * - 编辑器通过其配置目录（如 `~/.claude`）是否存在来自动检测。
 * - 默认使用软链接，仓库里的技能改动会即时生效；`--copy` 则复制一份。
 * - 只会操作本仓库中存在的技能名，不会碰编辑器里的其他技能。
 */

import { cpSync, existsSync, lstatSync, mkdirSync, readdirSync, readlinkSync, rmSync, symlinkSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const skillsRoot = join(repoRoot, 'skills')
const home = homedir()

interface Editor {
  id: string
  label: string
  configDir: string
  /** 可选别名，`--target` 时按产品名指定更顺手。 */
  aliases?: string[]
}

/**
 * 支持自动检测的编辑器：配置目录存在即视为已安装。
 * `configDir` 取自各客户端自己的用户目录名（Electron 应用可从 product.json 的 dataFolderName 查到）。
 */
const EDITORS: Editor[] = [
  { id: 'claude', label: 'Claude Code', configDir: join(home, '.claude') },
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
  const options: Options = { dryRun: false, copy: false, uninstall: false, help: false, targets: [], skills: [] }

  for (const arg of argv) {
    if (arg === '-n' || arg === '--dry-run')
      options.dryRun = true
    else if (arg === '--copy')
      options.copy = true
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

function listSkills(): string[] {
  return readdirSync(skillsRoot, { withFileTypes: true })
    .filter(entry => entry.isDirectory() && existsSync(join(skillsRoot, entry.name, 'SKILL.md')))
    .map(entry => entry.name)
    .sort()
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

function installSkills(options: Options): void {
  const allSkills = listSkills()
  if (allSkills.length === 0) {
    logError(`在 ${gray(skillsRoot)} 下没有找到任何技能（技能目录需包含 SKILL.md）`)
    process.exit(1)
  }

  const skills = options.skills.length > 0 ? pickSkills(allSkills, options.skills) : allSkills
  const editors = pickEditors(options.targets)

  if (editors.length === 0) {
    logWarn('未检测到任何受支持的编辑器，可用 `--target=claude,codebuddy,trae-cn,workbuddy` 显式指定')
    return
  }

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

      if (options.uninstall) {
        if (!pathExists(dest)) {
          logSkip(`跳过 ${name}（未安装）`)
          continue
        }
        if (!options.dryRun)
          rmSync(dest, { recursive: true, force: true })
        logOk(`移除 ${name}`)
        continue
      }

      const source = join(skillsRoot, name)

      if (!options.copy && isLinkedTo(dest, source)) {
        logSkip(`跳过 ${name}（软链接已指向仓库）`)
        continue
      }

      const existed = pathExists(dest)
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

    console.log('')
  }

  if (options.dryRun)
    logWarn('dry-run 模式：以上操作未真正执行')
}

function printHelp(): void {
  console.log(`${bold('用法')}：pnpm skills [选项]

${bold('选项')}
  --target=<ids>   只安装到指定编辑器，逗号分隔
                   可选: ${EDITORS.map(editor => editor.id).join(', ')}
                   别名: ${EDITORS.flatMap(editor => editor.aliases ?? []).join(', ')}
  --skill=<names>  只安装指定技能，逗号分隔
  --copy           复制文件而不是创建软链接
  --uninstall, -u  从各编辑器移除本仓库的技能
  --dry-run, -n    只打印将要执行的操作
  --help, -h       显示本帮助

${bold('示例')}
  pnpm skills
  pnpm skills --target=claude,codebuddy
  pnpm skills --target=traework-cn,workbuddy
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
