#!/usr/bin/env node
/**
 * 扫描中文稿件里的 AI 味候选表达。
 *
 * 为什么要有机械扫描：写作技能里的自查清单靠记忆执行，很容易被跳过；
 * 而「某个词有没有出现」是可以机械判定的。先把候选捞出来，再由作者回到上下文判断。
 * 命中不等于必须改——规则只是线索，承载实际信息的句子照原样保留。
 *
 * 用法：
 *   node scan-ai-tone.mjs 稿件.md [更多文件...]
 *   cat 稿件.md | node scan-ai-tone.mjs -
 */

import { readFileSync } from 'node:fs'
import { basename } from 'node:path'

// 每条规则只回答「这里可能有空话」，不回答「这一定是 AI 写的」。
// 词表刻意窄：泛词越多误报越多，误报会诱导作者删掉真实内容。
const RULES = [
  {
    name: '空话',
    pattern: /赋能|闭环|抓手|显著提升|至关重要|深入探讨|无缝衔接|全方位|多维度|助力|打造|极致|颠覆式|全新可能|值得一提的是|值得注意的是|需要指出的是|众所周知|不难发现/g,
  },
  {
    name: '拔高',
    pattern: /彰显了|标志着|见证了|开启了新篇章|迈上新台阶|注入新动能|再上新台阶|书写新篇章/g,
  },
  {
    name: '套话收尾',
    pattern: /综上所述|总而言之|总的来说|未来可期|拭目以待|希望对你有帮助|希望本文|如有疑问/g,
  },
  {
    name: '客服腔',
    pattern: /好问题|希望对您有帮助|请随时|感谢阅读|欢迎留言/g,
  },
  {
    name: '背景开头',
    pattern: /随着[^。！？\n]{0,16}(发展|进步|普及)/g,
  },
  {
    name: '假对比',
    pattern: /不仅(仅)?是[^。\n]{1,30}更是/g,
  },
]

const DASH = /——/g

/**
 * 跳过 YAML front-matter 与围栏代码块，避免把配置项和示例代码当成正文报出来。
 */
function isSkippable(line, state) {
  if (state.inFence) {
    if (/^\s*(```|~~~)/.test(line)) state.inFence = false
    return true
  }
  if (/^\s*(```|~~~)/.test(line)) {
    state.inFence = true
    return true
  }
  if (/^---\s*$/.test(line)) {
    state.inFrontMatter = !state.inFrontMatter
    return true
  }
  return state.inFrontMatter
}

/**
 * 去掉行内代码与链接地址后再匹配，否则 `赋能` 这类被引用的词也会命中。
 */
function stripInline(line) {
  return line
    .replace(/`[^`]*`/g, '')
    .replace(/\]\([^)]*\)/g, ']')
    .replace(/https?:\/\/\S+/g, '')
}

export function scan(text) {
  const hits = []
  const lines = text.split('\n')
  const state = { inFence: false, inFrontMatter: false }
  let dashTotal = 0

  lines.forEach((raw, index) => {
    if (isSkippable(raw, state)) return
    const line = stripInline(raw)

    for (const rule of RULES) {
      rule.pattern.lastIndex = 0
      const found = line.match(rule.pattern)
      if (found) {
        hits.push({
          line: index + 1,
          rule: rule.name,
          text: found.join('、'),
          excerpt: line.trim().slice(0, 60),
        })
      }
    }

    const dashes = line.match(DASH)
    if (dashes) {
      dashTotal += dashes.length
      // 一行里出现两个以上破折号，通常是在用标点代替句号。
      if (dashes.length > 1) {
        hits.push({
          line: index + 1,
          rule: '破折号',
          text: `本行 ${dashes.length} 个`,
          excerpt: line.trim().slice(0, 60),
        })
      }
    }
  })

  if (dashTotal > 3) {
    hits.push({
      line: 0,
      rule: '破折号',
      text: `全文 ${dashTotal} 个`,
      excerpt: '数量偏多，建议逐处换成逗号或句号',
    })
  }

  return hits
}

function report(name, hits) {
  if (hits.length === 0) {
    console.log(`${name}：没有命中候选。`)
    return
  }
  console.log(`${name}：`)
  for (const hit of hits) {
    const where = hit.line === 0 ? '  汇总' : `  ${String(hit.line).padStart(4)}:`
    console.log(`${where} [${hit.rule}] ${hit.text}`)
    console.log(`        ${hit.excerpt}`)
  }
  console.log(`  共 ${hits.length} 处候选。命中只是线索，回到上下文判断，承载信息的地方不动。`)
}

function main() {
  const args = process.argv.slice(2)
  if (args.length === 0) {
    console.error('用法：node scan-ai-tone.mjs <文件|-> [...]')
    process.exit(2)
  }

  for (const arg of args) {
    const text = arg === '-' ? readFileSync(0, 'utf8') : readFileSync(arg, 'utf8')
    report(arg === '-' ? 'stdin' : basename(arg), scan(text))
  }
}

main()
