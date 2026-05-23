---
name: game-asset-generator
description: Generates visual assets for games using CSS, SVG, or Unicode - sprites, icons, backgrounds, particles. Use when game needs better visuals or custom graphics.
argument-hint: "что нужно нарисовать (персонаж, враг, фон, иконка)"
---
# Game Asset Generator Skill

## Задача
Создаёт и интегрирует визуальные ассеты для игр. Главный путь — MiniMax image_generation в локальные PNG; процедурная графика только как fallback/эффекты.

## Инструменты
- **MiniMax image_generation** — background/title/sprite sheet PNG в `assets/`
- **Canvas drawImage** — основной способ рендера персонажей, врагов, машин и фонов
- **CSS/SVG/Canvas drawing** — частицы, свет, UI, fallback, мелкие декоративные элементы

## Примеры
- Пиксельный персонаж через CSS grid
- SVG зомби/робот/космический корабль
- Particle effects через Canvas
- Animated background через CSS keyframes

## Алгоритм
1. Определи что нужно нарисовать
2. Сформируй MiniMax prompt для PNG ассета
3. Сохрани ассет в `assets/`
4. Встрой в игру через `Image()` + `ctx.drawImage()`
5. Проверь, что ключевые объекты не являются цветными квадратами
6. Задеплой


<!-- Auto-improved 2026-04-16 -->
## Improvement Notes
- Add example showing 'surge.sh' in skill output
- Add example showing 'OK|ready|готова' in skill output
