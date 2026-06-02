import { expect, test } from '@playwright/test'

const apiBase = 'http://localhost:8000'

const treePayload = {
  nodes: [
    { id: 1, family_id: 1, member_id: 'I 1', name: 'Thomas Parent', relation: 'Father', role: 'Father', gender: 'M', age: 62, username: 'thomas', is_committee: false },
    { id: 2, family_id: 1, member_id: 'I 1W', name: 'Mary Parent', relation: 'Mother', role: 'Mother', gender: 'F', age: 59, username: 'mary', is_committee: false },
    { id: 3, family_id: 1, member_id: 'II 1', name: 'Anna Child', relation: 'Daughter', role: 'Daughter', gender: 'F', age: 32, username: 'anna', is_committee: false },
    { id: 3, family_id: 1, member_id: 'II 1-DUPE', name: 'Anna Child Duplicate', relation: 'Daughter', role: 'Daughter', gender: 'F', age: 32, username: 'anna-dupe', is_committee: false },
    { id: 4, family_id: 1, member_id: 'II 2', name: 'John Child', relation: 'Son', role: 'Son', gender: 'M', age: 29, username: 'john', is_committee: false },
    { id: 5, family_id: 2, member_id: 'III 1', name: 'Mia Grandchild', relation: 'Granddaughter', role: 'Granddaughter', gender: 'F', age: 6, username: 'mia', is_committee: false },
  ],
  edges: [
    { source: 1, target: 2, type: 'spouse' },
    { source: 2, target: 5, type: 'spouse' },
    { source: 1, target: 3, type: 'parent' },
    { source: 2, target: 3, type: 'parent' },
    { source: 1, target: 4, type: 'parent' },
    { source: 2, target: 4, type: 'parent' },
    { source: 3, target: 5, type: 'parent' },
  ],
  computed_relations: [],
  generation_depth: 0,
}

test.beforeEach(async ({ page }) => {
  await page.route(`${apiBase}/api/auth/me/`, async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        id: 101,
        username: 'thomas',
        email: 'thomas@example.test',
        name: 'Thomas Parent',
        member: 1,
      }),
    })
  })

  await page.route(`${apiBase}/api/families/tree/`, async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(treePayload),
    })
  })

  await page.route(`${apiBase}/api/profiles/community-roles/`, async (route) => {
    await route.fulfill({ contentType: 'application/json', body: '[]' })
  })
})

test('family tree renders spouse-aware layout with one co-parent connector per child', async ({ page }, testInfo) => {
  await page.goto('/familytree?view=visual')

  const nodes = page.locator('svg .nodes .node')
  const uniqueNodeCount = new Set(treePayload.nodes.map((node) => node.id)).size
  await expect(nodes).toHaveCount(uniqueNodeCount)

  const renderedIds = await nodes.evaluateAll((items) => items.map((item) => item.getAttribute('data-member-id')))
  expect(renderedIds).toEqual(Array.from(new Set(renderedIds)))

  await expect(page.locator('svg .spouse-links path')).toHaveCount(1)
  await expect(page.locator('svg .parent-links path')).toHaveCount(3)

  const annaConnector = page.locator('svg .parent-links path[data-child-id="3"]')
  const johnConnector = page.locator('svg .parent-links path[data-child-id="4"]')
  await expect(annaConnector).toHaveCount(1)
  await expect(johnConnector).toHaveCount(1)
  await expect(annaConnector).toHaveAttribute('data-parent-ids', /(^1,2$|^2,1$)/)
  await expect(johnConnector).toHaveAttribute('data-parent-ids', /(^1,2$|^2,1$)/)

  const connectorPaths = await page.locator('svg .parent-links path, svg .spouse-links path').evaluateAll((items) =>
    items.map((item) => item.getAttribute('d') || ''),
  )
  expect(connectorPaths.every((path) => !/[CQST]/.test(path))).toBe(true)

  const boxes = await nodes.evaluateAll((items) =>
    items.map((item) => {
      const box = (item as SVGGElement).getBBox()
      return { x: box.x, y: box.y, width: box.width, height: box.height }
    }),
  )
  for (let i = 0; i < boxes.length; i += 1) {
    for (let j = i + 1; j < boxes.length; j += 1) {
      const a = boxes[i]!
      const b = boxes[j]!
      const overlap =
        a.x < b.x + b.width &&
        a.x + a.width > b.x &&
        a.y < b.y + b.height &&
        a.y + a.height > b.y
      expect(overlap, `node ${i} overlaps node ${j}`).toBe(false)
    }
  }

  const screenshot = await page.locator('svg').screenshot()
  await testInfo.attach('familytree-svg.png', { body: screenshot, contentType: 'image/png' })
})
