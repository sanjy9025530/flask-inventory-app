from flask import Flask, render_template, request, redirect
import sqlite3
#---------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    query = request.args.get('query')
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    if query:
        cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()
    conn.close()
    return render_template('home.html', products=products)

#-------------------------------------------------------------------------------------------------------------------------

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        if not name or not price or not quantity:
            return "All fields are required!", 400

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            return "Price must be a number and quantity must be an integer", 400

        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
        conn.commit()
        conn.close()
        return redirect('/')
    
    return render_template('add_product.html')


#---------------------------------------------------------------------------------------------------------------------------------

@app.route('/locations')
def view_locations():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    conn.close()
    return render_template('location.html', locations=locations)

#----------------------------------------------------------------------------------------------------------------------------

@app.route('/add-location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location = request.form['location']
        if not location:
            return "Location name is required!", 400

        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO location(location) VALUES (?)", (location,))
        conn.commit()
        conn.close()
        return redirect('/locations')

    return render_template('add_location.html')

#--------------------------------------------------------------------------------------------------------------------------

@app.route('/edit-location/<int:id>', methods=['GET', 'POST'])
def edit_location(id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        location = request.form['location']
        cursor.execute("UPDATE location SET location=? WHERE location_id=?", (location, id))
        conn.commit()
        conn.close()
        return redirect('/locations')
    cursor.execute("SELECT * FROM location WHERE location_id=?", (id,))
    location = cursor.fetchone()
    conn.close()
    return render_template('edit_location.html', location=location)

#------------------------------------------------------------------------------------------------------------------------------

@app.route('/delete-location/<int:id>', methods=['POST'])
def delete_location(id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM location WHERE location_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/locations')

#--------------------------------------------------------------------------------------------------------------------------------

@app.route('/edit/<int:id>')
def edit_product(id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()
    conn.close()
    return render_template('edit.html', product=product)

#=============================================================================================================================


@app.route('/update/<int:id>', methods=['POST'])
def update_product(id):
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, price=?, quantity=? WHERE id=?", (name, price, quantity, id))
    conn.commit()
    conn.close()
    return redirect('/')

#==============================================================================================================================

@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

#=============================================================================================================================

@app.route('/movements')
def view_movements():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pm.movement_id, pm.timestamp, p.name, l1.location as from_location, l2.location as to_location, pm.qty
        FROM productmovement pm
        LEFT JOIN products p ON pm.product_id = p.id
        LEFT JOIN location l1 ON pm.from_location = l1.location_id
        LEFT JOIN location l2 ON pm.to_location = l2.location_id
    ''')
    movements = cursor.fetchall()
    conn.close()
    return render_template('movement.html', movements=movements)


#========================================================================================================================
@app.route('/add-movement', methods=['GET', 'POST'])
def add_movement():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        timestamp = request.form['timestamp']
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        product_id = request.form['product_id']
        qty = request.form['qty']

        cursor.execute('''
            INSERT INTO productmovement (timestamp, from_location, to_location, product_id, qty)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, from_location, to_location, product_id, qty))
        conn.commit()
        conn.close()
        return redirect('/movements')

    products = cursor.execute("SELECT * FROM products").fetchall()
    locations = cursor.execute("SELECT * FROM location").fetchall()
    conn.close()
    return render_template('add_movement.html', products=products, locations=locations)

#+============================================================================================================================================

@app.route('/edit-movement/<int:id>', methods=['GET', 'POST'])
def edit_movement(id):
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        timestamp = request.form['timestamp']
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        product_id = request.form['product_id']
        qty = request.form['qty']

        cursor.execute('''
            UPDATE productmovement
            SET timestamp = ?, from_location = ?, to_location = ?, product_id = ?, qty = ?
            WHERE movement_id = ?
        ''', (timestamp, from_location, to_location, product_id, qty, id))
        conn.commit()
        conn.close()
        return redirect('/movements')

    movement = cursor.execute("SELECT * FROM productmovement WHERE movement_id = ?", (id,)).fetchone()
    products = cursor.execute("SELECT * FROM products").fetchall()
    locations = cursor.execute("SELECT * FROM location").fetchall()
    conn.close()
    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
#=========================================================================================================================

@app.route('/delete-movement/<int:id>')
def delete_movement(id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productmovement WHERE movement_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/movements')

#=========================================================================================================================

@app.route('/report')
def stock_report():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT
        p.name AS product,
        l.location AS location,
        IFNULL(SUM(CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END), 0) -
        IFNULL(SUM(CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END), 0) AS balance
    FROM
        products p
    CROSS JOIN
        location l
    LEFT JOIN
        productmovement pm ON pm.product_id = p.id
    GROUP BY
        p.name, l.location
    HAVING
        balance != 0
    ORDER BY
        p.name, l.location
''')

    report = cursor.fetchall()
    conn.close()
    return render_template('report.html', report=report)

#========================================================================================================================



if __name__ == '__main__':
    app.run(debug=True)














