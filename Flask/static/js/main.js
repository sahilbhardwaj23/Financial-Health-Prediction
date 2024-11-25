// Form validation and enhancement
document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Number input formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Range slider value display
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const output = document.querySelector(`output[for="${input.id}"]`);
        if (output) {
            input.addEventListener('input', function() {
                output.textContent = this.value + '%';
            });
        }
    });
});

// Chart responsiveness
window.addEventListener('resize', function() {
    const charts = document.querySelectorAll('.chart-container');
    charts.forEach(chart => {
        if (chart.layout) {
            Plotly.relayout(chart, {
                width: chart.offsetWidth,
                height: chart.offsetHeight
            });
        }
    });
});

// Alert auto-dismiss
const alerts = document.querySelectorAll('.alert-dismissible');
alerts.forEach(alert => {
    setTimeout(() => {
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            closeButton.click();
        }
    }, 5000);
});