from flask import Flask, render_template, request, redirect, session,url_for, flash
import sqlite3
from applications.login_manager import *
from applications.categories_functions import *
from applications.cart_functions import *
from applications.user_info import *
from applications.search_functions import *
from applications.manager_functions import *
from applications.manager_coupons_functions import *
from applications.manager_summary_functions import *
from flask import current_app as app



@app.route('/manager/login', methods=['GET', 'POST'], endpoint='manager/login')
def manager_login_route():
    only_categories = get_categories();
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            manager_login(email, password)
            session['manager'] = email
            return redirect('/manager/dashboard')
        except Exception as e:
            print(str(e))
            return render_template('manager_login.html', only_categories=only_categories)
    
    return render_template('manager_login.html')

@app.route('/manager/logout', methods=['GET'])
def manager_logout():
    try:
        session.pop('manager', None)
        flash('Logged out. Visit us again.', 'success')
        return redirect('/')
    except Exception as e:
        return redirect('/manager/dashboard')

@app.route('/manager/dashboard', methods=['GET'])
def manager_dashboard_route():
    only_categories = get_categories();
    if 'manager' in session:
        try:
            categories = get_categories_with_products_from_db()            
            print(categories)
            return render_template('manager_dashboard.html', only_categories=only_categories, categories=categories)
        except Exception as e:
            flash(str(e))
    return redirect('/manager/login')

@app.route('/manager/summary', methods=['GET'])
def manager_summary_route():
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    
    try:
        bar_chart_data = generate_bar_chart()
        pie_chart_data = generate_pie_chart()
    
        return render_template('manager_summary.html', only_categories=only_categories, bar_chart_data=bar_chart_data, pie_chart_data=pie_chart_data)
        
    except Exception as e:
        flash(str(e))
        return redirect('/manager/dashboard')

@app.route('/manager/add_product', methods=['GET', 'POST'])
def add_product_route():
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    if request.method == 'GET':
        return render_template('add_product.html', only_categories=only_categories)
    
    if request.method == 'POST':
        try:
            product_name = request.form['product_name']
            category = request.form['category']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            unit = request.form['unit']
            manufacture_date = request.form['manufacture_date']
            expiry_date = request.form['expiry_date']
            
            add_product_to_category_in_db(category, product_name, quantity, manufacture_date, expiry_date, price, unit)
            
            flash(f"Product '{product_name}' added to the category.")
        
        except Exception as e:
            flash(str(e))
    return redirect('/manager/dashboard')

@app.route('/manager/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    try:
        if request.method == 'GET':
            product = get_product_by_id(product_id)
            return render_template('edit_product.html', product=product, only_categories=only_categories)
        
        if request.method == 'POST':
                # Retrieve the modified product information from the form
                product_name = request.form['product_name']
                category = request.form['category']
                quantity = int(request.form['quantity'])
                price = float(request.form['price'])
                unit = request.form['unit']
                manufacture_date = request.form['manufacture_date']
                expiry_date = request.form['expiry_date']
                
                # Update the product's information in the database
                update_product_in_db(product_id, product_name, category, quantity, price, unit, manufacture_date, expiry_date)
                
                flash(f"Product '{product_name}' updated successfully.")
            
    except Exception as e:
        flash(str(e))
    
    return redirect('/manager/dashboard') 
        

@app.route('/manager/delete_product/<int:product_id>', methods=['GET', 'POST'])
def remove_product_route(product_id):
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    
    if request.method == "GET":
        return render_template("delete_product.html", only_categories=only_categories)
    
    if request.method == 'POST':
        try:
            print(request.form)
            if "yes" in request.form:
                remove_product_from_db(product_id)
                flash("Deleted successfully.")
        except Exception as e:
            flash(str(e))
        return redirect('/manager/dashboard') 


@app.route('/manager/coupons', methods=['GET'])
def coupons():
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    
    try:
        coupons = get_coupon_codes_from_db()
        return render_template('manager_coupons.html', coupons=coupons, only_categories=only_categories)
    except Exception as e:
        flash(str(e))
        return redirect('/manager/dashboard')
    
@app.route('/manager/add_coupon', methods=['GET', 'POST'])
def add_coupon_route():
    only_categories = get_categories();
    if 'manager' not in session:
        return redirect('/manager/login')
    if request.method == 'GET':
        return render_template('add_coupon.html', only_categories=only_categories)
    
    if request.method == 'POST':
        try:
            coupon_code = request.form['coupon_code']
            discount = float(request.form['discount'])
            
            add_coupon_code_to_db(coupon_code, discount)
            
            flash(f"Coupon '{coupon_code}' added.")
        
        except Exception as e:
            flash(str(e))
    return redirect('/manager/coupons')

@app.route('/manager/delete_coupon/<coupon_code>', methods=['GET', 'POST'])
def remove_coupon_route(coupon_code):
    if 'manager' not in session:
        return redirect('/manager/login')
    
    if request.method == "GET":
        return render_template("delete_product.html")
    
    if request.method == 'POST':
        try:
            print(request.form)
            if "yes" in request.form:
                remove_coupon_code_from_db(coupon_code)
                flash("Deleted successfully.")
        except Exception as e:
            flash(str(e))
        return redirect('/manager/coupons') 

@app.route('/manager/categories/<categoryID>', methods=['GET'])
def category_products(categoryID):
    if 'manager' not in session:
        return redirect('/manager/login')
    try:
        only_categories = get_categories();
        categories_with_products = get_categories_with_products_from_db()
        products = []
        for category in categories_with_products:
            if category['categoryID'] == int(categoryID):
                category_name = category['category_name']
                products = category['products']
                break
        if products[0]['productID']==None: products=[] 
        return render_template('manager_category_products.html', only_categories=only_categories, products=products, category_name=category_name, categoryID= categoryID)
    except Exception as e:
        flash(str(e))
        return redirect('/manager/dashboard')
    
@app.route('/manager/categories/<categoryID>/delete_category', methods=['GET','POST'])
def remove_category(categoryID):
    if 'manager' not in session:
        return redirect('/manager/login')
    
    try:
        if request.method == "GET":
            return render_template("delete_product.html")
        
        if request.method == 'POST':
            if "yes" in request.form:
                remove_category_from_db(categoryID)
                flash("Deleted successfully.")
    except Exception as e:
        flash(str(e))
    return redirect('/manager/dashboard')

@app.route('/manager/categories/add_category', methods=['GET','POST'])
def add_category():
    if 'manager' not in session:
        return redirect('/manager/login')
    
    try:
            
            category_name = request.form['category_name']
            add_category_to_db(category_name)
            flash("Added successfully.")
    except Exception as e:
        flash(str(e))
    return redirect('/manager/dashboard')