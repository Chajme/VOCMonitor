
// Exporting chart as a PDF.
function exportChartAsPDF() {
    const canvas = document.getElementById('myChart');

    const canvasImage = canvas.toDataURL('image/png', 1.0);

    const pdf = new jsPDF('landscape');
    pdf.setFontSize(20);
    pdf.addImage(canvasImage, 'png', 10, 15, 280, 150);
    pdf.save('voc-chart.pdf');
}

// Exporting chart as an image.
function exportChartAsPNG() {
    const canvas = document.getElementById('myChart');
    const canvasImage = canvas.toDataURL('image/png', 1.0);

    const downloadLink = document.createElement('a');
    downloadLink.href = canvasImage;
    downloadLink.download = 'voc-chart.png';
    downloadLink.click();
}

// Button listener to reset chart zoom.
function attachEventHandlers(resetZoomFunction) {
    document.getElementById('resetZoom').addEventListener('click', resetZoomFunction);
}

function pauseFetchingHandler(pauseFetchingFunction) {
    document.getElementById('pauseFetching').addEventListener('click', pauseFetchingFunction);
}

export {
    exportChartAsPDF,
    exportChartAsPNG,
    attachEventHandlers,
    pauseFetchingHandler
};