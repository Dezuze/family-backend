import { computed } from 'vue'
import {
  FAMILY_RELATION_DEFINITIONS,
  type FamilyRelationDefinition,
  type FamilyRelationSide,
} from '../data/relations'

export type RelationshipSide = FamilyRelationSide

export interface ParsedRelationship {
  name: string
  offset: number
  side: RelationshipSide
  relation: string
  confidence: number
}

interface RelationPrototype {
  label: string
  offset: number
  side: RelationshipSide
  phrase: string
}

interface CompiledRelationPattern {
  regex: RegExp
  keyword: string
  relation: FamilyRelationDefinition
}

const MODEL_ID = 'Xenova/paraphrase-MiniLM-L3-v2'

const RELATION_PROTOTYPES: RelationPrototype[] = FAMILY_RELATION_DEFINITIONS.map((item) => ({
  label: item.label.toLowerCase(),
  offset: item.offset,
  side: item.side,
  phrase: `my ${item.label.toLowerCase()}`,
}))

const escapeRegex = (value: string): string => {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const keywordToRegex = (keyword: string): RegExp => {
  const pattern = keyword
    .trim()
    .split(/\s+/)
    .map((part) => escapeRegex(part))
    .join('\\s+')

  return new RegExp(`\\b${pattern}\\b`)
}

const RELATION_PATTERNS: CompiledRelationPattern[] = FAMILY_RELATION_DEFINITIONS
  .flatMap((relation) =>
    relation.keywords.map((keyword) => ({
      regex: keywordToRegex(keyword.toLowerCase()),
      keyword: keyword.toLowerCase(),
      relation,
    }))
  )
  .sort((a, b) => b.keyword.length - a.keyword.length)

let extractorPromise: Promise<any> | null = null
let prototypeVectorsPromise: Promise<Array<{ relation: RelationPrototype; vector: number[] }>> | null = null

const hasExplicitSide = (text: string): boolean => {
  return /(maternal|paternal|mother'?s|father'?s|mom'?s|dad'?s)/i.test(text)
}

const inferSide = (text: string, fallback: RelationshipSide = 'paternal'): RelationshipSide => {
  const lower = text.toLowerCase()
  if (/(maternal|mother'?s|mom'?s)/.test(lower)) return 'maternal'
  if (/(paternal|father'?s|dad'?s)/.test(lower)) return 'paternal'

  if (/(mother|mom|grandmother|grandma|daughter|granddaughter)/.test(lower)) return 'maternal'
  if (/(father|dad|grandfather|grandpa|son|grandson)/.test(lower)) return 'paternal'

  return fallback
}

const extractName = (text: string): string => {
  const trimmed = text.trim()

  const commaMatch = trimmed.match(/,\s*([\p{L}][\p{L}\s'.-]{0,60})$/u)
  if (commaMatch?.[1]) return commaMatch[1].trim()

  const namedMatch = trimmed.match(/\bnamed\s+([\p{L}][\p{L}\s'.-]{0,60})$/iu)
  if (namedMatch?.[1]) return namedMatch[1].trim()

  const trailingName = trimmed.match(/\b(?:this is|he is|she is)\s+my\b[^,]*\s([\p{Lu}][\p{L}'-]+(?:\s+[\p{Lu}][\p{L}'-]+){0,2})$/u)
  if (trailingName?.[1]) return trailingName[1].trim()

  return 'Unknown'
}

const countGreat = (text: string): number => {
  const matches = text.match(/great/g)
  return matches ? matches.length : 0
}

const extractOffsetHeuristic = (text: string): { offset: number | null; relation: string; sideHint?: RelationshipSide } => {
  const lower = text.toLowerCase()

  const nthGreatAncestor = lower.match(/(\d+)(?:st|nd|rd|th)?\s+great[-\s]*grand(?:father|mother|parent)/)
  if (nthGreatAncestor?.[1]) {
    const n = Number.parseInt(nthGreatAncestor[1], 10)
    return { offset: -(n + 2), relation: 'great-grandparent' }
  }

  const nthGreatDescendant = lower.match(/(\d+)(?:st|nd|rd|th)?\s+great[-\s]*grand(?:son|daughter|child)/)
  if (nthGreatDescendant?.[1]) {
    const n = Number.parseInt(nthGreatDescendant[1], 10)
    return { offset: n + 2, relation: 'great-grandchild' }
  }

  if (/(great[-\s]+)+grand(?:father|mother|parent)/.test(lower)) {
    return { offset: -(countGreat(lower) + 2), relation: 'great-grandparent' }
  }

  if (/(great[-\s]+)+grand(?:son|daughter|child)/.test(lower)) {
    return { offset: countGreat(lower) + 2, relation: 'great-grandchild' }
  }

  for (const rule of RELATION_PATTERNS) {
    if (rule.regex.test(lower)) {
      return {
        offset: rule.relation.offset,
        relation: rule.relation.relationClass,
        sideHint: rule.relation.side,
      }
    }
  }

  return { offset: null, relation: 'unknown' }
}

const toVector = (embedding: any): number[] => {
  if (!embedding) return []

  if (typeof embedding.tolist === 'function') {
    const list = embedding.tolist()
    if (Array.isArray(list) && Array.isArray(list[0])) return list[0] as number[]
    if (Array.isArray(list)) return list as number[]
  }

  if (Array.isArray(embedding)) {
    if (Array.isArray(embedding[0])) return embedding[0] as number[]
    return embedding as number[]
  }

  if (embedding.data) {
    return Array.from(embedding.data as Float32Array)
  }

  return []
}

const dot = (a: number[], b: number[]): number => {
  const len = Math.min(a.length, b.length)
  let sum = 0
  for (let i = 0; i < len; i += 1) {
    const av = a[i] ?? 0
    const bv = b[i] ?? 0
    sum += av * bv
  }
  return sum
}

const getExtractor = async (): Promise<any | null> => {
  if (!import.meta.client) return null

  if (!extractorPromise) {
    extractorPromise = (async () => {
      try {
        const transformers = await import('@xenova/transformers')
        transformers.env.useBrowserCache = true
        return transformers.pipeline('feature-extraction', MODEL_ID, {
          quantized: true,
        })
      } catch {
        return null
      }
    })()
  }

  return extractorPromise
}

const embedText = async (extractor: any, text: string): Promise<number[] | null> => {
  try {
    const out = await extractor(text, {
      pooling: 'mean',
      normalize: true,
    })
    const vector = toVector(out)
    return vector.length > 0 ? vector : null
  } catch {
    return null
  }
}

const getPrototypeVectors = async (): Promise<Array<{ relation: RelationPrototype; vector: number[] }>> => {
  if (!prototypeVectorsPromise) {
    prototypeVectorsPromise = (async () => {
      const extractor = await getExtractor()
      if (!extractor) return []

      const vectors: Array<{ relation: RelationPrototype; vector: number[] }> = []
      for (const relation of RELATION_PROTOTYPES) {
        const vector = await embedText(extractor, relation.phrase)
        if (vector) vectors.push({ relation, vector })
      }
      return vectors
    })()
  }

  return prototypeVectorsPromise
}

const classifyRelation = async (text: string): Promise<{ relation: RelationPrototype; score: number } | null> => {
  const extractor = await getExtractor()
  if (!extractor) return null

  const inputVector = await embedText(extractor, text)
  if (!inputVector) return null

  const prototypes = await getPrototypeVectors()
  if (prototypes.length === 0) return null

  let best: { relation: RelationPrototype; score: number } | null = null
  for (const item of prototypes) {
    const score = dot(inputVector, item.vector)
    if (!best || score > best.score) {
      best = { relation: item.relation, score }
    }
  }

  return best
}

export const useRelationshipParser = () => {
  const modelReady = computed(() => extractorPromise !== null)

  const warmup = async () => {
    await getExtractor()
    await getPrototypeVectors()
  }

  const parseRelationship = async (input: string): Promise<ParsedRelationship> => {
    const text = input.trim()
    if (!text) {
      return {
        name: 'Unknown',
        offset: 0,
        side: 'paternal',
        relation: 'unknown',
        confidence: 0,
      }
    }

    const heuristic = extractOffsetHeuristic(text)
    let offset = heuristic.offset
    let relation = heuristic.relation
    let confidence = 0.72

    let side = inferSide(text, heuristic.sideHint ?? 'paternal')

    if (offset === null || relation === 'unknown') {
      const semantic = await classifyRelation(text)
      if (semantic) {
        offset = offset ?? semantic.relation.offset
        relation = relation === 'unknown' ? semantic.relation.label : relation
        confidence = Math.max(confidence, Math.min(0.99, semantic.score))

        if (!hasExplicitSide(text)) {
          side = inferSide(text, semantic.relation.side)
        }
      }
    }

    if (offset === null) offset = 0

    return {
      name: extractName(text),
      offset,
      side,
      relation,
      confidence,
    }
  }

  return {
    parseRelationship,
    warmup,
    modelReady,
  }
}
