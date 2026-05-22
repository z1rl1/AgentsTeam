---
name: report-generation
description: Generate a structured research report combining theory, analysis results, charts, and conclusions. Use after analysis is complete to produce the final document.
triggers:
  - "доклад"
  - "отчёт"
  - "report"
  - "напиши доклад"
  - "исследование"
  - "оформи результаты"
---

# Report Generation Skill

## Report Structure

```
1. Введение (Introduction)
   - Тема и её актуальность
   - Цели исследования
   - Методология

2. Теоретическая часть
   - Описание темы/алгоритма/модели
   - Ключевые понятия
   - Математический аппарат (формулы)

3. Данные
   - Источник данных
   - Описание выборки (N записей, период, переменные)
   - Качество данных

4. Анализ и результаты
   - EDA результаты
   - Основные находки
   - Статистические показатели

5. Визуализации
   - Графики с подписями и интерпретацией
   - Ссылки на загруженные изображения

6. Выводы
   - Ответы на исследовательские вопросы
   - Практические рекомендации
   - Ограничения исследования

7. Список источников
```

## Format Rules
- Заголовки: `## Раздел`, `### Подраздел`
- Формулы: в кодблоке или LaTeX-нотации
- Таблицы: markdown tables
- Графики: ссылки на URL изображений
- Длина: 800-1500 слов (не считая таблиц)
- Язык: русский (если не указано иное)

## Upload & Link Charts
```bash
# Upload each chart and get URL
for file in ~/analytics_output/*.png; do
    url=$(curl -s -F "file=@$file" https://0x0.st)
    echo "$file → $url"
done
```

Include URLs inline in the report: `![График корреляции](URL)`

## Output
Markdown-formatted report ready to send in VK message.
All charts referenced as image URLs.
