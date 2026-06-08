# Outbreaker 2

## Overview

Here we use the output of the **outbreaker2** package for R to visualize a WIW network.

You can find the full tutorial of the pacakge [here](https://www.repidemicsconsortium.org/outbreaker2/articles/introduction.html).

---

## Input Data

The supported upload format is a `.rds` file which can easily be produced from R by using the `saveRDS()` function.

See below for how the example data was created from the fake outbreak that comes alongside the outbreaker package:

```R
library(outbreaker2)

dna <- fake_outbreak$dna
dates <- fake_outbreak$sample
ctd <- fake_outbreak$ctd
w <- fake_outbreak$w
data <- outbreaker_data(dna = dna, dates = dates, ctd = ctd, w_dens = w)

## we set the seed to ensure results won't change
set.seed(1)

res <- outbreaker(data = data)

saveRDS(res, file="fake_outbreaker.rds")
```

### Download Example Data

If you want to follow along the data can be downloaded here:

- [The input rds file](../assets/tutorial-data/outbreaker2.rds)
- [The additional metadata](../assets/tutorial-data/outbreaker2-transphylo-metadata.csv)

---
## Upload the rds file


![upload](../assets/screenshots/tutorials/outbreaker2/upload.png){: style="width:300px;"}

1. Select the outbreaker2 upload type
2. Drag and drop the rds file into the selection
3. Enter a label for the edges of the network
4. Confirm and upload the data

The resulting network should look like this:

![upload](../assets/screenshots/tutorials/outbreaker2/step0.png){: style="width:1300px;"}

---

In the Graph tab of the graph controls panel we can pick a different graph layout, 
here we pick the Euler layout (1).
Your graph should now look similar to this (2):

![upload](../assets/screenshots/tutorials/outbreaker2/step1.png){: style="width:1300px;"}

---

Next we select different edge settings:

![upload](../assets/screenshots/tutorials/outbreaker2/step2.png){: style="width:1300px;"}

1. Select the Edges tab in the graph control panel
2. Pick a different edge annotation label, here we pick posterior support
3. Change the position of the edge annotation label, here we pick follow edge
4. Change the scale width factor to increase or decrease the width of edges
    - Alternatively you can turn this off entirely 

---

Moving on to node settings:

![upload](../assets/screenshots/tutorials/outbreaker2/step3.png){: style="width:1300px;"}

1. Select the Nodes tab in the graph control panel
2. Select a label to be displayed on the nodes
3. Toggle on the color by label option

Further node options:

![upload](../assets/screenshots/tutorials/outbreaker2/step4.png){: style="width:1300px;"}

1. Expand the further options section
2. Turn on the option to suppress singleton, this removes isolated nodes from the graph
3. Change the node label font size

---

## Adding Metadata (Optional)

To add additional information to nodes we can upload a metadata `csv` file:

![upload](../assets/screenshots/tutorials/outbreaker2/step5.png){: style="width:300px;"}

1. Pick the metadata upload type in the upload section
2. Drag and drop your csv file into the selection
3. Select the name of the column in the csv file used to associate the data with nodes
4. Pick the existing node annotation to associate with the csv column picked in step 3.
5. Confirm and upload the additional data to your nodes

![upload](../assets/screenshots/tutorials/outbreaker2/step6.png){: style="width:1300px;"}



---
### Adding a legend

To keep track of all the colors we can add a legend node to the display by clicking on (1).

To improve the display one can drag and drop this legend into a better position.
Then clicking the Recenter graph button will focus the screen on the whole network.
These steps are indicated with the yellow highlights:

![upload](../assets/screenshots/tutorials/outbreaker2/step7.png){: style="width:1300px;"}

The resulting network should look similar to this:

![upload](../assets/screenshots/tutorials/outbreaker2/step8.png){: style="width:1300px;"}

---
