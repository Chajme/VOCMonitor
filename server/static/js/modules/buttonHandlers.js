

function exportChartAsPDF() {
    const canvas = document.getElementById('myChart');

    const canvasImage = canvas.toDataURL('image/png', 1.0);

    const pdf = new jsPDF('landscape');
    pdf.setFontSize(20);
    pdf.addImage(canvasImage, 'png', 10, 15, 280, 150);
    pdf.save('voc-chart.pdf');
}

function exportChartAsPNG() {
    const canvas = document.getElementById('myChart');
    const canvasImage = canvas.toDataURL('image/png', 1.0);

    const downloadLink = document.createElement('a');
    downloadLink.href = canvasImage;
    downloadLink.download = 'voc-chart.png';
    downloadLink.click();
}

function attachEventHandlers(resetZoomFunction) {
    document.getElementById('resetZoom').addEventListener('click', resetZoomFunction);
}

export {
    exportChartAsPDF,
    exportChartAsPNG,
    attachEventHandlers
};