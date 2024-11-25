// Update financial goals value display
const goalsSlider = document.getElementById('financial_goals_met');
const goalsValue = document.getElementById('goals-value');

if (goalsSlider) {
    goalsSlider.addEventListener('input', function() {
        goalsValue.textContent = this.value + '%';
    });
}

// Form validation
document.querySelector('.prediction-form')?.addEventListener('submit', function(e) {
    const inputs = this.querySelectorAll('input[type="number"]');
    let isValid = true;

    inputs.forEach(input => {
        if (input.value < 0) {
            alert('Please enter positive values only.');
            e.preventDefault();
            isValid = false;
            return;
        }
    });

    const income = parseFloat(document.getElementById('income').value);
    const expenses = parseFloat(document.getElementById('monthly_expenses').value);
    const loanPayments = parseFloat(document.getElementById('loan_payments').value);

    if (expenses + loanPayments > income) {
        alert('Total expenses and loan payments cannot exceed income.');
        e.preventDefault();
        isValid = false;
    }

    return isValid;
});

// Responsive chart handling
window.addEventListener('resize', function() {
    const gaugeChart = document.getElementById('gauge-chart');
    if (gaugeChart && gaugeChart.data) {
        Plotly.Plots.resize(gaugeChart);
    }
});