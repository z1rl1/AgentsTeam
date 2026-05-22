---
name: clustering
description: Apply clustering algorithms to find groups in data — K-Means, DBSCAN, hierarchical clustering. Includes optimal K selection, cluster visualization, and interpretation.
triggers:
  - "кластеризация"
  - "кластеры"
  - "clustering"
  - "K-means"
  - "группировка данных"
  - "сегментация"
---

# Clustering Skill

## Goal
Cluster the data, find optimal number of clusters, visualize results, interpret each cluster.

## Workflow

### 1. Preprocessing
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_numeric)
```

### 2. Find Optimal K (K-Means)
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

inertias = []
silhouettes = []
K_range = range(2, 11)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

# Plot elbow + silhouette → save as optimal_k.png
```

### 3. Apply Best Algorithm
- **K-Means**: clear spherical clusters, known K
- **DBSCAN**: arbitrary shape clusters, noise detection
- **Hierarchical**: dendrogram, unknown K

### 4. Visualize Clusters
```python
from sklearn.decomposition import PCA

# Reduce to 2D for visualization
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_scaled)

plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis', alpha=0.7)
# Save as clusters_2d.png
```

### 5. Interpret Clusters
- Mean of each feature per cluster
- What makes each cluster unique
- Cluster sizes and proportions
- Name clusters in plain language

## Output
- `optimal_k.png` — elbow + silhouette plots
- `clusters_2d.png` — PCA scatter colored by cluster
- `cluster_profiles.png` — heatmap of cluster means
- Text summary: cluster count, sizes, distinguishing features
