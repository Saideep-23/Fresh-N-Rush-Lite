Vue.component('product-item', {
    props: ['product'],
    data() {
        return {
            quantity: 1,
        };
    },
    methods: {
        addToCart() {
            // Calculate the total price based on the quantity
            const totalPrice = this.product.price * this.quantity;

            // Construct the cart item object
            const cartItem = {
                productID: this.product.productID,
                name: this.product.name,
                price: this.product.price,
                quantity: this.quantity,
                totalPrice: totalPrice,
            };

            // Emit the "add-to-cart" event with the cart item
            this.$emit('add-to-cart', cartItem);
        },
    },
    template: `
        <div class="product-item">
            <h3>{{ product.name }}</h3>
            <p>Price: {{ product.price }}</p>
            <input type="number" v-model="quantity" min="1">
            <p>Total Price: {{ product.price * quantity }}</p>
            <button @click="addToCart">Add to Cart</button>
        </div>
    `,
});

new Vue({
    el: '#app',
    data: {
        products: [],
        cartItems: [],
    },
    methods: {
        addToCart(cartItem) {
            this.cartItems.push(cartItem);
        },
    },
    mounted() {
        // Fetch the products data from the server
        fetch('/api/products')
            .then(response => response.json())
            .then(data => {
                this.products = data;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    },
});
