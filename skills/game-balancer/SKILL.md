---
name: game-balancer
description: Tunes game balance - enemy speed, spawn rate, player health, score multipliers, progression curve. Different from difficulty - this is fine-tuning parameters. Use when game feels unfair or unbalanced.
argument-hint: "slug игры и что именно нужно сбалансировать"
---
# Game Balancer Skill

## Задача
Тонкая настройка баланса игры: скорость врагов, здоровье, награды, прогрессия.

## Отличие от game-difficulty
- `game-difficulty` — грубо: лёгкий/средний/сложный
- `game-balancer` — тонко: точные числа, кривая прогрессии, ощущение fair play

## Параметры для балансировки
- Скорость врагов / препятствий
- Частота спауна
- Здоровье игрока
- Множители очков
- Скорость нарастания сложности
- Размер/зона хитбокса

## Алгоритм
1. Читай код, найди числовые константы
2. Определи что именно дисбалансировано
3. Измени значения, сохрани, задеплой


<!-- Auto-improved 2026-04-16 -->
## Improvement Notes
- Add example showing 'surge.sh' in skill output
- Add example showing 'OK|ready|готова' in skill output
