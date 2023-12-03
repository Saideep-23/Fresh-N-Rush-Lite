from applications.database import *

def get_categories():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    return categories

def get_products_by_category(category_id):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM products WHERE categoryID = ?", (category_id,))
        products = cursor.fetchall()
        
        cursor.close()
        return products
    except Exception as e:
        cursor.close()
        return None

def get_10_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return products
