$(document).ready(function() {
    $('.add_to_cart').on('click', function(e) {
        e.preventDefault();

        let product_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');

        console.log('Adding product to cart:', product_id);

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function() {
                        window.location = '/account/login/';
                    });
                } else if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else if (response.status == 'Success') {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + product_id).html(response.qty);
                    // Do not update the cart amount
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', xhr.responseText);
                var response = xhr.responseJSON;
                if (response && response.status == 'Failed' && response.message == 'Maximum limit reached for this product!') {
                    swal({
                        title: 'Maximum Limit Reached',
                        text: 'You have reached the maximum limit for this product.',
                        icon: 'warning',
                        button: 'OK'
                    });
                } else {
                    alert('Error: ' + (response ? response.message : 'Unknown error'));
                }
            }
        });
    });

    // Decrease cart
    $('.decrease_cart').on('click', function(e) {
        e.preventDefault();

        let product_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response);
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function() {
                        window.location.href = '/account/login';
                    });
                } else if (response.status == 'Failed') {
                    swal(response.message, '', 'error');
                } else if (response.status == 'Success') {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + product_id).html(response.qty);
                    // Do not update the cart amount

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(response.qty, product_id);
                        checkEmptyCart();
                    }
                }
            },
            error: function(xhr, status, error) {
                var response = xhr.responseJSON;
                alert('Error: ' + response.message);
            }
        });
    });


    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e) {
        e.preventDefault();

        let cart_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                console.log(response)
                if (response.status == 'Failed') {
                    swal(response.message, '', 'error')
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success")

                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                }
            }
        });
    });

    // delete the cart element if the qty is 0
    function removeCartItem(cartItemQty, cart_id) {
        if (cartItemQty <= 0) {
            // remove the cart item element
            $("#cart-item-" + cart_id).remove();
        }
    }

    // Check if the cart is empty
    function checkEmptyCart() {
        var cart_counter = parseInt($('#cart_counter').html());
        if (cart_counter === 0) {
            $("#empty-cart").css("display", "block");
        }
    }

    // apply cart amounts
    function applyCartAmounts(subtotal, tax_dict, grand_total) {
        if (window.location.pathname === '/shop/cart/') {
            // Update the cart amounts on the '/ecom/cart/' page
            $('#subtotal').html(subtotal);
            $('#total').html(grand_total);

            console.log(tax_dict)
        }
    }
});
