import { expect, test } from 'claude-code/testing'

const BACKDROP = {
  plugin: 'eco-8bit-weather',
  component: 'Backdrop',
  requestId: 'backdrop',
  props: { scene: 'eco-weather', plugin: 'eco-8bit-weather', glass: { blur: 12, tint: '#03182A', opacity: 0.35 } },
} as const

test('the look is set at session start with the weather scene', async ($, on) => {
  let set: unknown
  on('theme.set', (_, e) => {
    set = e
    return { value: { isDrawn: true, requestId: 'backdrop' } }
  })
  on('command.register', () => ({ value: { command: 'eco-theme' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'mobile', isInteractive: true })
  expect(set).toMatchObject({ backdrop: { scene: 'eco-weather' } })
})

test('the scene draws on mobile and desktop', async $ => {
  for (const surface of ['mobile', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BACKDROP, surface })
    const svg = await ui.find({ type: 'Svg' })
    expect(svg).toBeDefined()
    await ui.unmount()
  }
})

test('/eco-theme turns the look back on, and off', async ($, on) => {
  const calls: string[] = []
  on('theme.set', () => {
    calls.push('set')
    return { value: { isDrawn: true, requestId: 'backdrop' } }
  })
  on('theme.clear', () => {
    calls.push('clear')
    return { value: { isDrawn: false, reason: 'cleared' } }
  })
  const on1 = await $.command.run({ command: 'eco-theme', args: '' })
  const off = await $.command.run({ command: 'eco-theme', args: 'off' })
  expect(calls).toEqual(['set', 'clear'])
  expect(JSON.stringify(on1)).toContain('is on')
  expect(JSON.stringify(off)).toContain('is off')
})
