<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-500 hover:shadow-md md:p-6">
    <div class="flex flex-col gap-3 md:flex-row md:items-end">
      <div class="flex-1">
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
          {{ t('relationshipLab.labels.describeRelationship') }}
        </label>
        <input
          v-model="inputText"
          type="text"
          class="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none transition-all duration-300 focus:border-brand-gold focus:ring-2 focus:ring-brand-gold/20"
          :placeholder="t('relationshipLab.placeholders.relationshipInput')"
          @keyup.enter="addFromInput"
        />
      </div>

      <div class="flex items-center gap-3">
        <label class="flex items-center gap-2 text-xs text-slate-600">
          <input v-model="autoGhostBridges" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-brand-gold" />
          {{ t('relationshipLab.labels.autoGhostBridges') }}
        </label>

        <button
          class="rounded-xl bg-brand-gold px-4 py-2.5 text-sm font-bold text-white transition-all duration-300 hover:brightness-110 active:scale-95"
          @click="addFromInput"
        >
          {{ t('relationshipLab.actions.addMember') }}
        </button>
      </div>
    </div>

    <Transition name="fade-slide">
      <div v-if="parsedPreview" class="mt-3 rounded-xl border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-600">
        {{ t('relationshipLab.labels.parsed') }}: {{ parsedPreview }}
      </div>
    </Transition>

    <div class="mt-4 overflow-x-auto">
      <svg
        ref="svgRef"
        :width="width"
        :height="height"
        class="min-w-[720px] rounded-xl border border-slate-200 bg-linear-to-b from-slate-50 to-white"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRelationshipParser, type ParsedRelationship, type RelationshipSide } from '~/composables/useRelationshipParser.client'

interface TreeNode extends d3.SimulationNodeDatum {
  id: string
  name: string
  offset: number
  side: RelationshipSide
  ghost?: boolean
}

interface TreeLink extends d3.SimulationLinkDatum<TreeNode> {
  id: string
  source: string | TreeNode
  target: string | TreeNode
  ghost?: boolean
}

const width = 920
const height = 560
const generationHeight = 92

const svgRef = ref<SVGSVGElement | null>(null)
const { t } = useI18n()
const inputText = ref('')
const parsedPreview = ref<string>('')
const autoGhostBridges = ref(true)

const { parseRelationship, warmup } = useRelationshipParser()

const nodes = ref<TreeNode[]>([
  {
    id: 'user',
    name: t('relationshipLab.labels.userNode'),
    offset: 0,
    side: 'paternal',
    x: width / 2,
    y: height / 2,
    fx: width / 2,
    fy: height / 2,
  },
])

const links = ref<TreeLink[]>([])

let simulation: d3.Simulation<TreeNode, undefined> | null = null
let svg!: d3.Selection<SVGSVGElement, unknown, null, undefined>
let rowLayer!: d3.Selection<SVGGElement, unknown, null, undefined>
let linkLayer!: d3.Selection<SVGGElement, unknown, null, undefined>
let nodeLayer!: d3.Selection<SVGGElement, unknown, null, undefined>

const rowY = (offset: number): number => height / 2 + offset * generationHeight

const nodeIdFromLinkEnd = (value: string | TreeNode): string => {
  return typeof value === 'string' ? value : value.id
}

const linkExists = (sourceId: string, targetId: string): boolean => {
  return links.value.some((l) => {
    const s = nodeIdFromLinkEnd(l.source)
    const t = nodeIdFromLinkEnd(l.target)
    return s === sourceId && t === targetId
  })
}

const drawGenerationRows = () => {
  const offsets = nodes.value.map((n) => n.offset)
  const minOffset = Math.min(-4, ...offsets)
  const maxOffset = Math.max(4, ...offsets)

  const rows = d3.range(minOffset, maxOffset + 1)

  const rowLines = rowLayer
    .selectAll<SVGGElement, number>('g.row')
    .data(rows, (d) => String(d))

  const rowEnter = rowLines
    .enter()
    .append('g')
    .attr('class', 'row')

  rowEnter
    .append('line')
    .attr('x1', 12)
    .attr('x2', width - 12)
    .attr('stroke', '#e5e7eb')
    .attr('stroke-width', 1)

  rowEnter
    .append('text')
    .attr('x', 18)
    .attr('dy', -4)
    .attr('font-size', 10)
    .attr('fill', '#94a3b8')

  const rowMerge = rowEnter.merge(rowLines as any)
  rowMerge.select('line').attr('y1', (d) => rowY(d)).attr('y2', (d) => rowY(d))
  rowMerge.select('text').attr('y', (d) => rowY(d)).text((d) => `offset ${d}`)

  rowLines.exit().remove()
}

const renderGraph = () => {
  drawGenerationRows()

  const linkSel = linkLayer
    .selectAll<SVGLineElement, TreeLink>('line.tree-link')
    .data(links.value, (d) => d.id)

  linkSel
    .enter()
    .append('line')
    .attr('class', 'tree-link')
    .attr('stroke-width', 1.6)
    .merge(linkSel as any)
    .attr('stroke', (d) => (d.ghost ? '#cbd5e1' : '#d4af37'))
    .attr('stroke-dasharray', (d) => (d.ghost ? '4 4' : '0'))
    .attr('x1', (d) => (d.source as TreeNode).x ?? width / 2)
    .attr('y1', (d) => (d.source as TreeNode).y ?? rowY(0))
    .attr('x2', (d) => (d.target as TreeNode).x ?? width / 2)
    .attr('y2', (d) => (d.target as TreeNode).y ?? rowY(0))

  linkSel.exit().remove()

  const nodeSel = nodeLayer
    .selectAll<SVGGElement, TreeNode>('g.tree-node')
    .data(nodes.value, (d) => d.id)

  const nodeEnter = nodeSel
    .enter()
    .append('g')
    .attr('class', 'tree-node')
    .call(
      d3
        .drag<SVGGElement, TreeNode>()
        .on('start', (event, d) => {
          if (!simulation) return
          if (!event.active) simulation.alphaTarget(0.2).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = rowY(d.offset)
        })
        .on('end', (event, d) => {
          if (!simulation) return
          if (!event.active) simulation.alphaTarget(0)
          if (d.id === 'user') {
            d.fx = width / 2
            d.fy = rowY(0)
          } else {
            d.fx = null
            d.fy = null
          }
        })
    )

  nodeEnter
    .append('circle')
    .attr('r', (d) => (d.id === 'user' ? 18 : d.ghost ? 11 : 13))
    .attr('stroke-width', 2)

  nodeEnter
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', 28)
    .attr('font-size', 11)
    .attr('font-weight', 700)

  const nodeMerge = nodeEnter.merge(nodeSel as any)

  nodeMerge
    .select('circle')
    .attr('fill', (d) => {
      if (d.id === 'user') return '#1f2937'
      if (d.ghost) return '#f8fafc'
      return d.side === 'maternal' ? '#fce7f3' : '#fef3c7'
    })
    .attr('stroke', (d) => {
      if (d.id === 'user') return '#111827'
      if (d.ghost) return '#cbd5e1'
      return d.side === 'maternal' ? '#db2777' : '#b45309'
    })

  nodeMerge
    .select('text')
    .attr('fill', (d) => (d.ghost ? '#64748b' : '#0f172a'))
    .text((d) => d.name)

  nodeMerge.attr('transform', (d) => `translate(${d.x ?? width / 2}, ${d.y ?? rowY(d.offset)})`)

  nodeSel.exit().remove()
}

const restartSimulation = () => {
  if (!simulation) return

  const linkForce = simulation.force('link') as d3.ForceLink<TreeNode, TreeLink> | undefined
  linkForce?.links(links.value)

  simulation.nodes(nodes.value)
  simulation.alpha(0.85).restart()
}

const addGhostBridge = (target: TreeNode) => {
  if (!autoGhostBridges.value) return
  if (target.offset === 0) return

  const step = target.offset > 0 ? 1 : -1
  let previousId = 'user'

  for (let generation = step; generation !== target.offset; generation += step) {
    const ghostId = `ghost-${target.side}-${generation}`

    if (!nodes.value.some((n) => n.id === ghostId)) {
      nodes.value.push({
        id: ghostId,
        name: `ghost ${generation}`,
        offset: generation,
        side: target.side,
        ghost: true,
        x: width / 2 + (Math.random() - 0.5) * 80,
        y: rowY(generation),
      })
    }

    if (!linkExists(previousId, ghostId)) {
      links.value.push({
        id: `ghost-link-${previousId}-${ghostId}`,
        source: previousId,
        target: ghostId,
        ghost: true,
      })
    }

    previousId = ghostId
  }

  if (!linkExists(previousId, target.id)) {
    links.value.push({
      id: `ghost-link-${previousId}-${target.id}`,
      source: previousId,
      target: target.id,
      ghost: true,
    })
  }
}

const addParsedMember = (parsed: ParsedRelationship) => {
  const nodeId = `node-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`

  const newNode: TreeNode = {
    id: nodeId,
    name: parsed.name || t('relationshipLab.labels.unknown'),
    offset: parsed.offset,
    side: parsed.side,
    x: width / 2 + (Math.random() - 0.5) * 140,
    y: rowY(parsed.offset),
  }

  nodes.value.push(newNode)

  links.value.push({
    id: `direct-${nodeId}`,
    source: 'user',
    target: nodeId,
  })

  addGhostBridge(newNode)
  restartSimulation()
}

const addFromInput = async () => {
  const text = inputText.value.trim()
  if (!text) return

  const parsed = await parseRelationship(text)
  parsedPreview.value = JSON.stringify(parsed)
  addParsedMember(parsed)
  inputText.value = ''
}

onMounted(async () => {
  await warmup()

  if (!svgRef.value) return

  svg = d3.select(svgRef.value)
  rowLayer = svg.append('g').attr('class', 'rows')
  linkLayer = svg.append('g').attr('class', 'links')
  nodeLayer = svg.append('g').attr('class', 'nodes')

  simulation = d3
    .forceSimulation<TreeNode>(nodes.value)
    .force(
      'link',
      d3
        .forceLink<TreeNode, TreeLink>(links.value)
        .id((d) => d.id)
        .distance(84)
        .strength(0.6)
    )
    .force('charge', d3.forceManyBody<TreeNode>().strength(-210))
    .force('x', d3.forceX<TreeNode>(width / 2).strength(0.06))
    .force('y', d3.forceY<TreeNode>((d) => rowY(d.offset)).strength(1))
    .force('collide', d3.forceCollide<TreeNode>(24))
    .on('tick', () => {
      for (const node of nodes.value) {
        if (node.id === 'user') {
          node.x = width / 2
          node.y = rowY(0)
          node.fx = width / 2
          node.fy = rowY(0)
        } else {
          node.y = rowY(node.offset)
        }
      }
      renderGraph()
    })

  renderGraph()
})

onBeforeUnmount(() => {
  simulation?.stop()
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
