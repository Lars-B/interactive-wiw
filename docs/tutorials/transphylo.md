# Transphylo

## Overview

Here we use the output of the **TransPhylo** package for R to visualize a WIW network.

You can find the full tutorial of the pacakge [here]().

---

## Input Data

The supported upload format is a `.rds` file which can easily be produced from R by using the `saveRDS()` function.

See below for how the example data was created from a random tree using the `ape` package `rtree` function:

```R
library(ape)
library(TransPhylo)

set.seed(42)
phy <- rtree(n=30, rooted=T)
ptree <- ptreeFromPhylo(phy, dateLastSample=1916.42)
w.shape <- 10
w.scale <- 0.1
res <- inferTTree(ptree, mcmcIterations=1000,w.shape=w.shape,w.scale=w.scale)

saveRDS(res, file="random_transphylo.rds")

mat <- computeMatWIW(res, burnin=0.2)

saveRDS(mat, file="random_transphylo_mat.rds")
```

### Download Example Data

If you want to follow along the data can be downloaded here:

- [The MCMC input rds file](../assets/tutorial-data/random_transphylo.rds)
- [The Matrix input rds file](../assets/tutorial-data/random_transphylo_mat.rds)
- [The additional metadata](../assets/tutorial-data/outbreaker2-transphylo-metadata.csv)

---
## Step 1: Upload the rds file

todo