const fs = require('fs')
const path = require('path')
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)])
const files = walk('app').filter((f) => f.endsWith('.vue'))
const suspects = []
for (const file of files) {
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/)
  lines.forEach((line, idx) => {
    const l = line.trim()
    if (!l) return
    const textMatch = l.match(/>([^<{}][^<]*[A-Za-z][^<]*)</)
    if (textMatch && !l.includes("t('") && !l.includes('t("')) suspects.push(`${file}:${idx+1}: ${l}`)
    const attrRe = /(placeholder|title|aria-label|alt|label)=\"([^\"]*[A-Za-z][^\"]*)\"/g
    if (attrRe.test(l) && !l.includes(':placeholder') && !l.includes(':title') && !l.includes(':aria-label') && !l.includes(':alt')) suspects.push(`${file}:${idx+1}: ${l}`)
  })
}
console.log(`suspects=${suspects.length}`)
for (const line of [...new Set(suspects)]) console.log(line)
