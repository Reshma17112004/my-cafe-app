import sqlite3
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hardcoded menu items
MENU_ITEMS = {
    "1": {"name": "Chocolate Cake", "category": "Dessert", "price": 120},
    "2": {"name": "Ice Cream", "category": "Dessert", "price": 80},
    "3": {"name": "Cold Coffee", "category": "Drink", "price": 90},
    "4": {"name": "Lemonade", "category": "Drink", "price": 60},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html', items=MENU_ITEMS)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    if item_id in cart:
        cart[item_id]['quantity'] += quantity
    else:
        cart[item_id] = {
            'name': name,
            'price': price,
            'quantity': quantity
        }

    session['cart'] = cart
    return ('', 204)  # Avoid page reload

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        name = request.form['customer_name']
        mobile = request.form['customer_mobile']
        return render_template('bill.html', cart=cart, total=total, name=name, mobile=mobile)

    return render_template('checkout.html', total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    # Format cart as string
    items_str = "; ".join([f"{item['name']} x {item['quantity']}" for item in cart.values()])

    # Insert into DB
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (name, mobile, items, total)
        VALUES (?, ?, ?, ?)
    ''', (name, mobile, items_str, total))
    conn.commit()
    conn.close()

    # Clear cart after placing order
    session.pop('cart', None)

    return render_template('success.html', name=name, mobile=mobile)

@app.route('/admin/orders')
def admin_orders():
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY timestamp DESC')
    orders = cursor.fetchall()
    conn.close()
    return render_template('admin_orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
