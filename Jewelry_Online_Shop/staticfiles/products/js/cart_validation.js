document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[action*="cart_add"]');
    const quantityInput = document.querySelector('#quantity-input');
    const maxStock = {{ product.stock }};  // Replace with the actual stock quantity from your Django context

    form.addEventListener('submit', function(event) {
        const selectedQuantity = parseInt(quantityInput.value, 10);

        if (selectedQuantity > maxStock) {
            event.preventDefault();  // Prevent form submission
            alert('You cannot add more than ' + maxStock + ' items to your cart.');
        }
    });
});
