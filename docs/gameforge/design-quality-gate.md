# GameForge Design Quality Gate

This document translates external game UI/UX, accessibility, canvas image, and game-feel guidance into concrete rules for the GameForge agent system.

## Source-Derived Principles

1. Text must be readable during gameplay, not just present.
   - Microsoft Xbox Accessibility Guideline 101 emphasizes text size, face, weight, spacing, alignment, case, and color as separate readability dimensions.
   - XAG 102 emphasizes contrast between HUD/text and the background, especially because gameplay backgrounds constantly change.
   - Encoding for agents: require readable font stack, HUD panels/overlays, text outline/shadow only where useful, and no tiny/debug-looking UI.

2. Contrast is a gameplay requirement.
   - HUD, health, score, prompts, menus, and important symbols need strong contrast against moving/noisy backgrounds.
   - Encoding for agents: no raw text directly on noisy generated key art unless there is a translucent panel, dark/light scrim, stroke, or shadow that preserves legibility.

3. Images must preserve aspect ratio.
   - CSS object-fit cover/contain exists specifically to avoid stretching media; fill stretches/squeezes when aspect ratios differ.
   - Canvas drawImage supports source rectangles: `drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight)`, which is the right primitive for crop/cover/sprite-sheet rendering.
   - Encoding for agents: require `drawCover`, `drawContain`, or equivalent source-rectangle crop helpers for full-screen/key art; reject blind `drawImage(img, 0, 0, canvas.width, canvas.height)` for generated art.

4. Game screens need layers and hierarchy.
   - Game engines commonly separate background, midground, gameplay objects, foreground, and HUD layers; HUD should be an overlay layer, not mixed randomly into gameplay objects.
   - Encoding for agents: require named rendering passes/layers and clear draw order: background -> parallax/midground -> gameplay -> effects -> HUD -> modal/menu.

5. Visual hierarchy should match gameplay importance.
   - Score, health, objective, remaining lives, level progress, and interaction prompts should not all compete equally.
   - Encoding for agents: require HUD grouping, size hierarchy, spacing, and stable screen regions. Avoid giant floating labels over gameplay unless it is a momentary result screen.

6. Game feel comes from synchronized feedback.
   - Research on game feel describes moment-to-moment interaction as intentional affective design; juicing amplifies events with visuals/audio/timing so actions feel clear and satisfying.
   - Encoding for agents: require event-specific feedback bundles: animation + sound + particles + optional short screen shake/hit-stop for important impacts, not constant noise.

7. Generated assets are raw material, not final design.
   - AI key art can be visually inconsistent, noisy, or poorly framed. The game must crop, layer, tint, mask, and compose it rather than paste it full-screen.
   - Encoding for agents: generated image use must be deliberate: crop actors from sprite sheets, use background as layered scenery or title art, add overlays/lighting/UI separately.

## Agent Prompt Contract

Every GameForge generation prompt must include:

- Use `MiniMax-M2.7` for game code and MiniMax image/music assets for visuals/audio.
- Preserve aspect ratio for all generated images.
- Implement `drawCover`/`drawContain`/sprite crop helpers before drawing generated PNGs.
- Use `assets/background.png`/`assets/title.png` only through aspect-safe composition, never blind stretch.
- Use `assets/sprites.png` through cropped regions for actors, enemies, vehicles, props, pickups, and bosses.
- UI must use readable sans/system font stack, not global crude pixel monospace.
- Important text must live on panels, scrims, or outlined/shadowed regions with clear contrast.
- Render in layers: background, parallax/midground, gameplay, effects, HUD, menu/modal.
- No debug-looking HUD, giant neon labels, overlapping text, or raw text pasted onto noisy image areas.
- Include game feel: particles, short proportional screen shake, animation states, audio feedback, and state transitions.

## Static QA Rules

The static playtester should fail deploy when:

- Generated images exist but are not used with `Image()`/`drawImage()`.
- Generated images are drawn full-screen by blind stretching without crop/cover/contain helpers.
- Primary actors are still rectangle-only.
- UI lacks readable typography signals: system/sans font stack, panels/overlays, text alignment, shadows/outlines, or hierarchy.
- HUD/menu composition lacks grouped score/health/lives/objective/progress/control regions.
- Code has too few draw calls, entities, visual systems, or feedback systems.

## Visual QA Roadmap

Static QA cannot fully judge taste. The next upgrade should run a browser screenshot pass and ask a vision-capable reviewer to score:

- Does the first screen look like a finished game, not a prototype?
- Are generated assets distorted, blurry, badly cropped, or visually incompatible?
- Is text readable at desktop and mobile sizes?
- Does UI overlap gameplay or fight the art?
- Do actors look like intentional sprites rather than placeholders?
- Would a human reasonably want to play for several minutes?

## References

- Microsoft Xbox Accessibility Guideline 101: Text display — https://learn.microsoft.com/gaming/accessibility/xbox-accessibility-guidelines/101
- Microsoft Xbox Accessibility Guideline 102: Contrast — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102
- MDN Canvas `drawImage()` — https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage
- MDN Canvas tutorial: Using images — https://developer.mozilla.org/docs/Web/API/Canvas_API/Tutorial/Using_images
- CSS object-fit behavior — https://css-tricks.com/almanac/properties/o/object-fit/
- Material Design typography — https://m1.material.io/style/typography.html
- Construct layers/parallax/HUD documentation — https://www.construct.net/en/construct-2/manuals/construct-2/project-primitives/layers
- Game Feel survey — https://arxiv.org/abs/2011.09201
