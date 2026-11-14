# Eco 8-Bit Weather theme

A Claude Code theme for the Claude desktop and mobile apps. A pixel-art Eco logo sits in the middle of the screen while a pickup, a box truck and a van drive past a row of houses along the bottom. The weather cycles on a 60-second loop: rain (with lightning and lit windows), then sun (with birds), then wind (gusts, blowing leaves, swaying trees).

The app's own surfaces use Eco navy, with cyan as the accent and lime for success. Themes don't show in the terminal.

## Use it

```
claude --plugin-dir ./eco-8bit-weather-theme
```

In a session the desktop app starts, set `CLAUDE_CODE_PLUGIN_DIRS` to this folder's absolute path instead.

## Change the scene

`hooks/scene.ts` is generated. Edit `source/gen_scene.py`, then run it from `source/` (needs Python with Pillow):

```
python3 gen_scene.py 60 scene.svg
```

and wrap the output as `export const SCENE: string = "<svg…>"` in `hooks/scene.ts`. The first argument is the loop length in seconds. Keep the SVG under 131,072 characters.
