if (!window._tooltipFollowMouse) {
    window._tooltipFollowMouse = true;

    document.addEventListener('mousemove', function(e) {
        const tooltip = document.getElementById('node-tooltip');
        const graph = document.getElementById('cytoscape');

        if (!tooltip || !graph) return;

        const graphRect = graph.getBoundingClientRect();

        const insideGraph =
            e.clientX >= graphRect.left &&
            e.clientX <= graphRect.right &&
            e.clientY >= graphRect.top &&
            e.clientY <= graphRect.bottom;

        // Hide tooltip when outside the graph
        if (!insideGraph) {
            tooltip.style.display = 'none';
            return;
        }

        // Only position the tooltip when it is visible
        if (tooltip.style.display === 'block') {
            const offset = 15;
            const tooltipRect = tooltip.getBoundingClientRect();

            // Default: place tooltip to the right of the cursor
            let left = e.clientX + offset;

            // If it would go off the right side of the screen,
            // place it to the left of the cursor instead
            if (left + tooltipRect.width > window.innerWidth) {
                left = e.clientX - tooltipRect.width - offset;
            }

            // Default: place tooltip below the cursor
            let top = e.clientY + offset;

            // If it would go off the bottom of the screen,
            // place it above the cursor instead
            if (top + tooltipRect.height > window.innerHeight) {
                top = e.clientY - tooltipRect.height - offset;
            }

            // Prevent the tooltip from going off the left/top edges
            left = Math.max(0, left);
            top = Math.max(0, top);

            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
        }
    });
}