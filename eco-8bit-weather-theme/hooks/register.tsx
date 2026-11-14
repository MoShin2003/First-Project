import type { Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { SCENE } from './scene'

const SCENE_NAME = 'eco-weather'

// Eco navy for the app's own surfaces; the backdrop carries the weather.
const { theme, problems } = makeColors({
  label: 'Eco 8-Bit Weather',
  only: 'dark',
  roles: { accent: '#00A3D8', success: '#84BD00', warning: '#F8B82A', danger: '#E5484D', pro: '#E94E8B' },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#03182A',
        'surface-1': '#082237',
        'surface-2': '#0C2A42',
        'surface-3': '#11304A',
        'text-primary': '#F1F6FA',
        'text-secondary': '#C2D3E1',
        'text-muted': '#93AABD',
      },
    },
  },
})

// A navy veil keeps white chat text readable over the sunny sky.
const LOOK: ThemeSetArgs = {
  colors: theme,
  backdrop: { scene: SCENE_NAME, glass: { blur: 12, tint: '#03182A', opacity: 0.35 } },
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    const set = await $.theme.set(LOOK)

    if (!set.isDrawn) {
      $.ui.status(set.reason)
    }

    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if ((e.surface !== 'desktop' && e.surface !== 'mobile') || e.props.scene !== SCENE_NAME) {
      return next(e)
    }

    const { Svg } = $.ui.resolve(e)

    return (
      <Svg
        source={SCENE}
        alt="Eco trucks driving past a pixel-art neighborhood while the weather turns from rain to sun to wind"
        isInteractive
      />
    )
  })
}
