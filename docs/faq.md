# Frequently Asked Questions

??? question "My network has to many edges and I cannot see anything..."

    You might want to set the [edge threshold](interface-overview.md#advanced-edge-options) 
    a bit higher to reduce the amount of edges. Typically 0.1 is a good value to start with.
    If you have a set of MST edges use the [edge display selection](interface-overview.md#edge-settings)
    to only select the MST edges and use the "Dagre (Hierarchical)" graph layout to get started.

??? question "Why can't I see any edges?"

    Check that your filters, in particular the edge [threshold selection](interface-overview.md#advanced-edge-options) is not set too high.

??? question "Why does my graph reload when I change the layout?"
    
    As soon as you change the layout the program has to recompute where to best place the nodes and edges, which results in a reload.
    This possibly rearranges the nodes differently than they were before.

??? question "What does WIW stand for?"
    
    This is an abbreviation of who-infected-whom and referst to the person to person transmissions.

??? question "What are indirect edges?"

    Both BREATH and transphylo model unsampled cases in the data.
    We say that A indirectly infects B if the infector of B is not known and A is the most recently
    sampled infector of A. In other words, A infects some unsampled individual which might
    infect other unknown individuals until one of these infects B.

??? question "What is MST and what are the MST edges?"

    If your full network is connected, i.e. there are not multiple components in your WIW network,
    then the MST (maximum spanning tree) is the highest probable infection scenario that does not
    contain a circle.
