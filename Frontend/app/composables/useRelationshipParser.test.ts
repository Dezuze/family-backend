import { describe, expect, it } from 'vitest'
import { FAMILY_RELATION_DEFINITIONS } from '../data/relations'
import { useRelationshipParser } from './useRelationshipParser.client'

describe('useRelationshipParser', () => {
  const relationCases = FAMILY_RELATION_DEFINITIONS.map((item) => ({
    relationLabel: item.label,
    phrase: `This is my ${item.label.toLowerCase()}, Thomas`,
    offset: item.offset,
    relation: item.relationClass,
    side: item.side,
  }))

  it('parses father relationship with offset -1', async () => {
    const { parseRelationship } = useRelationshipParser()

    const parsed = await parseRelationship('This is my father, Thomas')

    expect(parsed.name).toBe('Thomas')
    expect(parsed.offset).toBe(-1)
    expect(parsed.side).toBe('paternal')
    expect(parsed.relation).toBe('parent')
  })

  it('parses grandfather relationship with offset -2', async () => {
    const { parseRelationship } = useRelationshipParser()

    const parsed = await parseRelationship('This is my grandfather, Thomas')

    expect(parsed.name).toBe('Thomas')
    expect(parsed.offset).toBe(-2)
    expect(parsed.side).toBe('paternal')
    expect(parsed.relation).toBe('grandparent')
  })

  it('parses nth great-grandfather relationship with correct generation offset', async () => {
    const { parseRelationship } = useRelationshipParser()

    const parsed = await parseRelationship('This is my 2nd great-grandfather, Thomas')

    expect(parsed.name).toBe('Thomas')
    expect(parsed.offset).toBe(-4)
    expect(parsed.side).toBe('paternal')
    expect(parsed.relation).toBe('great-grandparent')
  })

  it('supports all configured relation labels from user perspective', async () => {
    const { parseRelationship } = useRelationshipParser()

    for (const testCase of relationCases) {
      const parsed = await parseRelationship(testCase.phrase)
      expect(parsed.name, `${testCase.relationLabel}: expected name`).toBe('Thomas')
      expect(parsed.offset, `${testCase.relationLabel}: expected offset`).toBe(testCase.offset)
      expect(parsed.relation, `${testCase.relationLabel}: expected relation`).toBe(testCase.relation)
      expect(parsed.side, `${testCase.relationLabel}: expected side`).toBe(testCase.side)
    }
  })
})