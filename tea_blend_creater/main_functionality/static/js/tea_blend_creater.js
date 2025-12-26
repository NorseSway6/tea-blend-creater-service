function updatePriceValue(value) {
    document.getElementById('priceValue').textContent = value + ' руб.';
}
    
document.addEventListener('DOMContentLoaded', function() {
    const priceSlider = document.getElementById('{{ form.price_range.id_for_label }}');
    if (priceSlider) {
        updatePriceValue(priceSlider.value);
            
        priceSlider.addEventListener('input', function() {
            updatePriceValue(this.value);
        });
    }
});

document.getElementById('blendForm').addEventListener('submit', function(e) {
    const submitBtn = this.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Генерируем...';
    submitBtn.disabled = true;
});