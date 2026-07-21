if (!window._tooltipFollowMouse) {
    window._tooltipFollowMouse = true;
    document.addEventListener('mousemove', function(e) {
        const tooltip = document.getElementById('node-tooltip');
        if (tooltip && tooltip.style.display === 'block') {
            tooltip.style.left = (e.clientX + 15) + 'px';
            tooltip.style.top = (e.clientY + 15) + 'px';
        }
    });
}