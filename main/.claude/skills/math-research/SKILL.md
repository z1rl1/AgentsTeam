---
name: math-research
description: Research and implement any mathematical algorithm or economic model — explain theory, implement in Python, run on example data, visualize results. Use for academic topics like TCO, optimization algorithms, graph theory, ML algorithms from scratch.
triggers:
  - "алгоритм"
  - "изучи"
  - "объясни"
  - "реализуй"
  - "математическая модель"
  - "экономическая модель"
  - "теория"
  - "метод"
---

# Math Research Skill

## Goal
Given any mathematical/algorithmic topic, produce:
1. Clear theoretical explanation
2. Working Python implementation
3. Visual demonstration on real/synthetic data
4. Practical interpretation

## Workflow

### 1. Theory (200-400 words)
- What problem does it solve?
- Core idea in plain language
- Key formula(s) with explanation of each variable
- Historical context / who invented it and why

### 2. Implementation
```python
# Always implement from scratch first (educational)
# Then show scikit-learn/scipy equivalent if available

def algorithm_name(params):
    """
    Clean, commented implementation.
    Each step explained in comments.
    """
    # Step 1: ...
    # Step 2: ...
    return result

# Example usage with synthetic data
import numpy as np
np.random.seed(42)
data = np.random.randn(100)
result = algorithm_name(data)
```

### 3. Visualization
- Show the algorithm working (before/after, convergence, etc.)
- If optimization: plot cost function over iterations
- If classification: decision boundary
- If graph: draw the graph with networkx
- Save all plots to `~/analytics_output/`

### 4. Real Example
- Find or generate realistic data for the topic
- Apply the algorithm
- Interpret results in domain terms

### 5. Practical Takeaways
- When to use this vs alternatives
- Strengths and limitations
- Common mistakes

## TCO Example
For Transaction Cost Optimization/Economics:
- Explain Coase theorem, Williamson's framework
- Model: TC = Production costs + Transaction costs
- Variables: asset specificity, uncertainty, frequency
- Implement optimization model
- Plot cost curves, efficient boundaries
