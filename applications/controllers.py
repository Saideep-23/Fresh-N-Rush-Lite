from flask import Flask, render_template, request, redirect, session,url_for, flash, g
from applications.login_manager import *
from applications.categories_functions import *
from applications.cart_functions import *
from applications.user_info import *
from applications.search_functions import *
from applications.database import *
from flask import current_app as app
from datetime import date



@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        try:
            products = get_10_products()
            categories = get_categories()
            
            if 'email' in session:
                email = session['email']
                user = get_user(email)
                name = user[1]
                return render_template('index.html', user=name, signed=True, products=products, categories=categories)
            else:
                return render_template('index.html', user="", signed=False, products=products, categories=categories)
        except Exception as e:
            flash(str(e))
            return render_template('index.html', user="", signed=False, products=[], categories=[])
    else:
        if 'email' not in session:
            flash("You must be logged in to add products to the cart.", "error")
            return redirect(url_for('login_route'))
        
        email = session['email']
        product_id = request.form['product']
        quantity = request.form['count']
        
        if quantity == "":
            flash("You need to add an integer value, greater than 0")
            return redirect(url_for('index'))
        elif int(quantity) <= 0:
            flash("Quantity should be a positive number.")
            return redirect(url_for('index'))
        else:
            quantity = int(quantity)
        
        print(product_id, quantity)
        
        try:
            insert_cart_item(email, product_id, quantity)
            flash("Product added to the cart successfully.", "success")
        except Exception as e:
            flash(str(e), "error")
        
        return redirect(url_for('index'))
    

@app.route('/shopping_cart', methods=['GET', 'POST'], endpoint='shopping_cart')
def shopping_cart():
    categories = get_categories()
    if 'email' not in session:
        return redirect(url_for('login_route'))
    
    email = session['email']
    totalPrice = 0;
    try:
        cart_items = fetch_cart_items_by_email(email)
        for (name, price, quantity, productID) in cart_items:
            totalPrice += price * quantity

        email = session['email']
        user = get_user(email)
        name = user[1]

        coupon_code = request.form.get('coupon_code')
        if coupon_code:
            try:
                discount_percentage = apply_coupon(email, coupon_code)
                if discount_percentage is not None:
                    totalPrice -= totalPrice * (discount_percentage / 100)
                    flash('Coupon code applied')
            except Exception as e:
                flash(str(e), "error")
                return redirect('/shopping_cart')

        formatted_total_price = "{:.2f}".format(totalPrice)
        return render_template('shopping_cart.html', user=name,cart_items=cart_items, totalPrice=formatted_total_price, signed=True, categories=categories)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('index'))

@app.route('/shopping_cart/update_product/<int:product_id>', methods=['GET','POST'])
def update_product(product_id):
    if 'email' not in session:
        return redirect(url_for('/'))
    email = session['email']
    try:
        quantity = request.form['count']
        if quantity == "": quantity = 0
        else: quantity = float(quantity)
        update_cart_item(email, product_id, quantity)
        flash("Product quantity updated successfully.", "success")
    except Exception as e:
        flash(str(e), "error")
    
    return redirect(url_for('shopping_cart'))

@app.route('/shopping_cart/delete_product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    if 'email' not in session:
        return redirect(url_for('/'))
    
    email = session['email']
    try:
        delete_cart_item(email, product_id)
        flash("Product deleted from the cart successfully.", "success")
    except Exception as e:
        flash(str(e), "error")
    
    return redirect(url_for('shopping_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'email' not in session:
        flash("You must be logged in to checkout.", "error")
        return redirect('/')
    email = session['email']
    categories = get_categories()
    cart_items = fetch_cart_items_by_email(email)

    try:
        print(cart_items)
        totalPrice = float(request.form['totalPrice'])
        print(totalPrice)
        order_date = str(date.today())

        update_inventory()
        record_order(email, order_date, cart_items, totalPrice)
        empty_cart(email)
        
        return render_template('order_confirmation.html', signed=True, cart_items=cart_items, totalPrice=totalPrice, categories=categories)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('shopping_cart'))


@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login_route():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login(email, password)
            session['email'] = email
            return redirect('/')
        except Exception as e:
            flash(str(e))
            return redirect('/login')
    return render_template('login.html')

@app.route('/dashboard')
def user_dashboard():
    if 'email' not in session:
        return redirect(url_for('login_route'))
    
    email = session['email']
    
    try:
        categories = get_categories()
        user_info = fetch_user_info(email)
        user_orders = fetch_order_history(email)
        return render_template('user_dashboard.html', categories=categories, user_info=user_info, signed=True, user_orders=user_orders)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'], endpoint='signup')
def signup_route():
    if request.method == 'POST':
        try:
            name = request.form["name"]
            phone_number = request.form["phoneno"]
            address = request.form["address"]
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if not name or not phone_number or not address or not email or not password:
                raise Exception("All fields are required")
            elif not validate_email(email):  
                raise Exception("Valid email required")
            elif not validate_phone_number(phone_number): 
                raise Exception("Valid phone number required")
            elif password != confirm_password:
                raise Exception("Password fields do not match")
            else:
                signup(email, password)
                add_user_info(email, name, phone_number, address)
                return redirect('/login')
        except Exception as e:
            flash(str(e))
            return redirect('/signup')
    
    return render_template('signup.html')

@app.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    try:
        session.pop('email', None)
        flash('Logged out. Visit us again.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('index'))



@app.route('/category/<int:category_id>', methods=['GET', 'POST'])
def products_by_category(category_id):
    if request.method == "GET":
        try:
            categories = get_categories()
            products = get_products_by_category(category_id)
            if 'email' in session:
                email = session['email']
                user = get_user(email)
                name = user[1]
                return render_template('index.html', user=name, signed=True, products=products, categories=categories)
            else:
                return render_template('index.html', user="", signed=False, products=products, categories=categories)
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
    else:
        if 'email' not in session:
            flash("You must be logged in to add products to the cart.", "error")
            return redirect(url_for('login_route'))
        
        email = session['email']
        product_id = request.form['product']
        
        quantity = request.form['count']
        if quantity == "":
            flash("You need to add an integer value, greater than 0")
            return redirect(url_for('index'))
        elif int(quantity) <= 0:
            flash("Quantity should be a positive number.")
            return redirect(url_for('index'))
        else:
            quantity = int(quantity)
        
        print(product_id, quantity)
        
        try:
            insert_cart_item(email, product_id, quantity)
            flash("Product added to the cart successfully.", "success")
        except Exception as e:
            flash(str(e))
        
        return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    
    categories = get_categories()
    if request.method == 'POST':
        if request.form.get('action') == 'search':
            if 'email' not in session:
                logged_in = False
                email=""
                name=""
            else:
                logged_in = True
                email = session['email']
                user = get_user(email)
                name = user[1]
            try:
                search_query = request.form['search_query']
                
                min_price = request.form.get('min_price')
                max_price = request.form.get('max_price')
                if min_price == '':
                    min_price = 0
                if max_price == '':
                    max_price = float('inf')
                
                min_manufacture_date = request.form.get('min_manufacture_date', '')
                max_manufacture_date = request.form.get('max_manufacture_date', '')
                min_expiry_date = request.form.get('min_expiry_date', '')
                max_expiry_date = request.form.get('max_expiry_date', '')
                exclude_out_of_stock = request.form.get('exclude_out_of_stock')
                
                product_results = search_products_in_db(search_query.lower(), min_price, max_price,
                                                        min_manufacture_date, max_manufacture_date,
                                                        min_expiry_date, max_expiry_date, exclude_out_of_stock)
                if product_results:

                    return render_template('index.html', user=name, products=product_results, signed=logged_in, categories=categories)
                
                category_results = search_categories_in_db(search_query.lower())
                
                print("search_categories in db", category_results)
                
                if category_results:

                    products_in_category = get_products_by_category_search(category_results, min_price, max_price,
                                                        min_manufacture_date, max_manufacture_date,
                                                        min_expiry_date, max_expiry_date)
                    print("products in category")
                    return render_template('index.html', user=name,category_results=category_results, products=products_in_category, signed=logged_in, categories=categories)
                
                return render_template('index.html', user=name, no_results=True)
            except Exception as e:
                flash(f'Something went wrong: {e}')
                return redirect(url_for('index'))
        
        else:
            try:
                if 'email' not in session:
                    flash("You must be logged in to add products to the cart.", "error")
                    return redirect(url_for('login_route'))
                
                email = session['email']
                product_id = request.form['product']
                quantity = request.form['count']
                
                if quantity == "":
                    flash("You need to add an integer value, greater than 0")
                    return redirect(url_for('index'))
                elif int(quantity) <= 0:
                    flash("Quantity should be a positive number.")
                    return redirect(url_for('index'))
                else:
                    quantity = int(quantity)
                            
                insert_cart_item(email, product_id, quantity)
                flash("Product added to the cart successfully.", "success")
            except Exception as e:
                flash(str(e), "error")
            
            return redirect(url_for('index'))