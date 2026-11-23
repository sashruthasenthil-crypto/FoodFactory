from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from models import User
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import( db, Customer,Product, Supplier, RawMaterial, BOMItem, StockTransaction, ProductionBatch )

app = Flask(__name__)

app.config['SECRET_KEY'] = 'foodfactory-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodfactory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
db.init_app(app)

with app.app_context():
    db.create_all()


# Dashboard
@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')
    if user and user.check_password(password):
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))


# View and Search Customers
@app.route('/customers')
@login_required
def customers():
    search = request.args.get('search', '').strip()

    query = Customer.query

    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        )

    all_customers = query.order_by(Customer.id.desc()).all()

    return render_template(
        'customers.html',
        customers=all_customers,
        search=search
    )


# Add Customer
@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not name:
            flash('Customer name is required.', 'danger')
            return redirect(url_for('add_customer'))

        new_customer = Customer(
            name=name,
            email=email or None,
            phone=phone or None,
            address=address or None
        )

        db.session.add(new_customer)
        db.session.commit()

        flash('Customer added successfully!', 'success')

        return redirect(url_for('customers'))

    return render_template('add_customer.html')


# Edit Customer
@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):

    customer = db.get_or_404(Customer, id)

    if request.method == 'POST':

        name = request.form.get('name', '').strip()

        if not name:
            flash('Customer name is required.', 'danger')
            return redirect(url_for('edit_customer', id=id))

        customer.name = name
        customer.email = request.form.get('email', '').strip() or None
        customer.phone = request.form.get('phone', '').strip() or None
        customer.address = request.form.get('address', '').strip() or None

        db.session.commit()

        flash('Customer updated successfully!', 'success')

        return redirect(url_for('customers'))

    return render_template(
        'edit_customer.html',
        customer=customer
    )


# Delete Customer
@app.route('/delete_customer/<int:id>', methods=['POST'])
@login_required
def delete_customer(id):

    customer = db.get_or_404(Customer, id)

    db.session.delete(customer)
    db.session.commit()

    flash('Customer deleted successfully!', 'success')

    return redirect(url_for('customers'))


# View and Search Products
@app.route('/products')
@login_required
def products():

    search = request.args.get('search', '').strip()

    query = Product.query

    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%')
        )

    all_products = query.order_by(Product.id.desc()).all()

    return render_template(
        'products.html',
        products=all_products,
        search=search
    )


# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        try:
            price = float(request.form.get('price', ''))
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Enter a valid non-negative price.', 'danger')
            return redirect(url_for('add_product'))

        if not name:
            flash('Product name is required.', 'danger')
            return redirect(url_for('add_product'))

        new_product = Product(
            name=name,
            category=category or None,
            price=price,
            description=description or None
        )

        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')

        return redirect(url_for('products'))

    return render_template('add_product.html')


# Edit Product
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):

    product = db.get_or_404(Product, id)

    if request.method == 'POST':

        name = request.form.get('name', '').strip()

        try:
            price = float(request.form.get('price', ''))
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Enter a valid non-negative price.', 'danger')
            return redirect(url_for('edit_product', id=id))

        if not name:
            flash('Product name is required.', 'danger')
            return redirect(url_for('edit_product', id=id))

        product.name = name
        product.category = request.form.get('category', '').strip() or None
        product.price = price
        product.description = request.form.get('description', '').strip() or None

        db.session.commit()

        flash('Product updated successfully!', 'success')

        return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)


# Delete Product
@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):

    product = db.get_or_404(Product, id)

    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully!', 'success')

    return redirect(url_for('products'))

# View and Search Suppliers
@app.route('/suppliers')
@login_required
def suppliers():

    search = request.args.get('search', '').strip()

    query = Supplier.query

    if search:
        query = query.filter(
            db.or_(
                Supplier.name.ilike(f'%{search}%'),
                Supplier.phone.ilike(f'%{search}%')
            )
        )

    all_suppliers = query.order_by(Supplier.id.desc()).all()

    return render_template(
        'suppliers.html',
        suppliers=all_suppliers,
        search=search
    )


# Add Supplier
@app.route('/add_supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()

        if not name:
            flash('Supplier name is required.', 'danger')
            return redirect(url_for('add_supplier'))

        new_supplier = Supplier(
            name=name,
            phone=phone or None,
            email=email or None,
            address=address or None
        )

        db.session.add(new_supplier)
        db.session.commit()

        flash('Supplier added successfully!', 'success')

        return redirect(url_for('suppliers'))

    return render_template('add_supplier.html')


# Edit Supplier
@app.route('/edit_supplier/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):

    supplier = db.get_or_404(Supplier, id)

    if request.method == 'POST':

        name = request.form.get('name', '').strip()

        if not name:
            flash('Supplier name is required.', 'danger')
            return redirect(url_for('edit_supplier', id=id))

        supplier.name = name
        supplier.phone = request.form.get('phone', '').strip() or None
        supplier.email = request.form.get('email', '').strip() or None
        supplier.address = request.form.get('address', '').strip() or None

        db.session.commit()

        flash('Supplier updated successfully!', 'success')

        return redirect(url_for('suppliers'))

    return render_template(
        'edit_supplier.html',
        supplier=supplier
    )


# Delete Supplier
@app.route('/delete_supplier/<int:id>', methods=['POST'])
@login_required
def delete_supplier(id):

    supplier = db.get_or_404(Supplier, id)

    # Prevent deletion if raw materials use this supplier
    if RawMaterial.query.filter_by(supplier_id=id).first():
        flash(
            'Cannot delete this supplier because raw materials are linked to it.',
            'danger'
        )
        return redirect(url_for('suppliers'))

    db.session.delete(supplier)
    db.session.commit()

    flash('Supplier deleted successfully!', 'success')

    return redirect(url_for('suppliers'))
# View Raw Materials
@app.route('/materials')
@login_required
def materials():
    search = request.args.get('search', '').strip()

    query = RawMaterial.query

    if search:
        query = query.filter(
            or_(
                RawMaterial.name.ilike(f'%{search}%'),
                RawMaterial.category.ilike(f'%{search}%')
            )
        )

    materials_list = query.order_by(RawMaterial.id.desc()).all()

    return render_template(
        'materials.html',
        materials=materials_list,
        search=search
    )


# Add Raw Material
@app.route('/add_material', methods=['GET', 'POST'])
@login_required
def add_material():
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        unit = request.form.get('unit', '').strip()
        supplier_id = request.form.get('supplier_id', '').strip()

        try:
            quantity = float(request.form.get('quantity', ''))
            minimum_stock = float(request.form.get('minimum_stock', '0'))

            if not name or quantity < 0 or minimum_stock < 0:
                raise ValueError

            supplier = None

            if supplier_id:
                supplier = db.session.get(Supplier, int(supplier_id))

                if supplier is None:
                    raise ValueError

            material = RawMaterial(
                name=name,
                category=category,
                quantity=quantity,
                unit=unit,
                minimum_stock=minimum_stock,
                supplier=supplier
            )

            db.session.add(material)
            db.session.commit()

            flash('Raw material added successfully!', 'success')
            return redirect(url_for('materials'))

        except (ValueError, TypeError):
            flash('Enter valid, non-negative quantities and supplier details.', 'danger')

    return render_template('add_material.html', suppliers=suppliers)


# Edit Raw Material
@app.route('/edit_material/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_material(id):
    material = db.get_or_404(RawMaterial, id)
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            quantity = float(request.form.get('quantity', ''))
            minimum_stock = float(request.form.get('minimum_stock', '0'))
            supplier_id = request.form.get('supplier_id', '').strip()

            if not name or quantity < 0 or minimum_stock < 0:
                raise ValueError

            supplier = None

            if supplier_id:
                supplier = db.session.get(Supplier, int(supplier_id))

                if supplier is None:
                    raise ValueError

            material.name = name
            material.category = request.form.get('category', '').strip()
            material.quantity = quantity
            material.unit = request.form.get('unit', '').strip()
            material.minimum_stock = minimum_stock
            material.supplier = supplier

            db.session.commit()

            flash('Raw material updated successfully!', 'success')
            return redirect(url_for('materials'))

        except (ValueError, TypeError):
            flash('Enter valid, non-negative quantities and supplier details.', 'danger')

    return render_template(
        'edit_material.html',
        material=material,
        suppliers=suppliers
    )


# Delete Raw Material
@app.route('/delete_material/<int:id>', methods=['POST'])
@login_required
def delete_material(id):
    material = db.get_or_404(RawMaterial, id)

    db.session.delete(material)
    db.session.commit()

    flash('Raw material deleted successfully!', 'success')

    return redirect(url_for('materials'))
# View Bill of Materials
@app.route('/bom')
@login_required
def bom():
    bom_items = BOMItem.query.order_by(BOMItem.id.desc()).all()

    return render_template(
        'bom.html',
        bom_items=bom_items
    )


# Add BOM Item
@app.route('/add_bom', methods=['GET', 'POST'])
@login_required
def add_bom():
    products = Product.query.order_by(Product.name).all()
    materials = RawMaterial.query.order_by(RawMaterial.name).all()

    if request.method == 'POST':
        try:
            product_id = int(request.form.get('product_id', ''))
            material_id = int(request.form.get('raw_material_id', ''))
            quantity = float(request.form.get('quantity_required', ''))

            product = db.session.get(Product, product_id)
            material = db.session.get(RawMaterial, material_id)

            if product is None or material is None or quantity <= 0:
                raise ValueError

            existing = BOMItem.query.filter_by(
                product_id=product_id,
                raw_material_id=material_id
            ).first()

            if existing:
                flash('This raw material is already added to this product.', 'warning')
                return redirect(url_for('add_bom'))

            item = BOMItem(
                product_id=product_id,
                raw_material_id=material_id,
                quantity_required=quantity
            )

            db.session.add(item)
            db.session.commit()

            flash('BOM item added successfully!', 'success')
            return redirect(url_for('bom'))

        except (ValueError, TypeError):
            flash('Please select valid product and material and enter a positive quantity.', 'danger')

    return render_template(
        'add_bom.html',
        products=products,
        materials=materials
    )


# Edit BOM Item
@app.route('/edit_bom/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bom(id):
    item = db.get_or_404(BOMItem, id)

    products = Product.query.order_by(Product.name).all()
    materials = RawMaterial.query.order_by(RawMaterial.name).all()

    if request.method == 'POST':
        try:
            product_id = int(request.form.get('product_id', ''))
            material_id = int(request.form.get('raw_material_id', ''))
            quantity = float(request.form.get('quantity_required', ''))

            product = db.session.get(Product, product_id)
            material = db.session.get(RawMaterial, material_id)

            if product is None or material is None or quantity <= 0:
                raise ValueError

            duplicate = BOMItem.query.filter(
                BOMItem.product_id == product_id,
                BOMItem.raw_material_id == material_id,
                BOMItem.id != id
            ).first()

            if duplicate:
                flash('This material is already added to this product.', 'warning')
                return redirect(url_for('edit_bom', id=id))

            item.product_id = product_id
            item.raw_material_id = material_id
            item.quantity_required = quantity

            db.session.commit()

            flash('BOM item updated successfully!', 'success')
            return redirect(url_for('bom'))

        except (ValueError, TypeError):
            flash('Please enter valid details and a positive quantity.', 'danger')

    return render_template(
        'edit_bom.html',
        item=item,
        products=products,
        materials=materials
    )


# Delete BOM Item
@app.route('/delete_bom/<int:id>', methods=['POST'])
@login_required
def delete_bom(id):
    item = db.get_or_404(BOMItem, id)

    db.session.delete(item)
    db.session.commit()

    flash('BOM item deleted successfully!', 'success')

    return redirect(url_for('bom'))
# View Inventory
@app.route('/inventory')
@login_required
def inventory():
    materials = RawMaterial.query.order_by(
        RawMaterial.name
    ).all()

    transactions = StockTransaction.query.order_by(
        StockTransaction.id.desc()
    ).limit(20).all()

    return render_template(
        'inventory.html',
        materials=materials,
        transactions=transactions
    )


# Record Stock In / Stock Out
@app.route('/stock_transaction/<int:id>', methods=['GET', 'POST'])
@login_required
def stock_transaction(id):
    material = db.get_or_404(RawMaterial, id)

    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        note = request.form.get('note', '').strip()

        try:
            quantity = float(request.form.get('quantity', ''))

            if quantity <= 0:
                raise ValueError

            if transaction_type == 'Stock In':
                material.quantity += quantity

            elif transaction_type == 'Stock Out':
                if quantity > material.quantity:
                    flash('Insufficient stock! Available quantity: ' + str(material.quantity), 'danger')
                    return redirect(url_for('stock_transaction', id=id))

                material.quantity -= quantity

            else:
                raise ValueError

            transaction = StockTransaction(
                raw_material_id=material.id,
                transaction_type=transaction_type,
                quantity=quantity,
                note=note
            )

            db.session.add(transaction)
            db.session.commit()

            flash('Stock transaction recorded successfully!', 'success')
            return redirect(url_for('inventory'))

        except (ValueError, TypeError):
            flash('Please enter a valid positive quantity and transaction type.', 'danger')

    return render_template(
        'stock_transaction.html',
        material=material
    )
# View Production
@app.route('/production')
@login_required
def production():
    batches = ProductionBatch.query.order_by(
        ProductionBatch.id.desc()
    ).all()

    return render_template(
        'production.html',
        batches=batches
    )


# Add Production
@app.route('/add_production', methods=['GET', 'POST'])
@login_required
def add_production():

    products = Product.query.order_by(Product.name).all()

    if request.method == 'POST':

        try:
            product_id = int(request.form.get('product_id', ''))
            quantity = float(request.form.get('quantity', ''))

            product = db.session.get(Product, product_id)

            if product is None or quantity <= 0:
                raise ValueError

            bom_items = BOMItem.query.filter_by(
                product_id=product_id
            ).all()

            if not bom_items:
                flash('No BOM is available for this product.', 'danger')
                return redirect(url_for('add_production'))

            # Check stock availability before deduction
            for item in bom_items:

                required = item.quantity_required * quantity

                if item.raw_material.quantity < required:
                    flash(
                        'Insufficient stock for ' +
                        item.raw_material.name,
                        'danger'
                    )
                    return redirect(url_for('add_production'))

            # Deduct raw materials and record Stock Out transactions
            for item in bom_items:

                required = item.quantity_required * quantity

                item.raw_material.quantity -= required

                transaction = StockTransaction(
                    raw_material_id=item.raw_material.id,
                    transaction_type='Stock Out',
                    quantity=required,
                    note='Used for production of ' + product.name
                )

                db.session.add(transaction)

            # Save production record
            batch = ProductionBatch(
                product_id=product_id,
                quantity=quantity
            )

            db.session.add(batch)

            db.session.commit()

            flash('Production completed successfully!', 'success')

            return redirect(url_for('production'))

        except (ValueError, TypeError):
            db.session.rollback()
            flash('Please enter valid production details.', 'danger')

        except Exception:
            db.session.rollback()
            flash('Production could not be completed. Please try again.', 'danger')

    return render_template(
        'add_production.html',
        products=products
    )
# Reports and Analytics
@app.route('/reports')
@login_required
def reports():

    # Total counts
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_suppliers = Supplier.query.count()
    total_materials = RawMaterial.query.count()

    # Low stock materials
    low_stock_materials = RawMaterial.query.filter(
        RawMaterial.quantity <= RawMaterial.minimum_stock
    ).all()

    # Production records
    production_batches = ProductionBatch.query.order_by(
        ProductionBatch.id.desc()
    ).all()

    total_production = sum(
        batch.quantity for batch in production_batches
    )

    # Recent stock transactions
    transactions = StockTransaction.query.order_by(
        StockTransaction.id.desc()
    ).limit(10).all()

    # All raw materials
    materials = RawMaterial.query.order_by(
        RawMaterial.name
    ).all()

    return render_template(
        'reports.html',
        total_customers=total_customers,
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_materials=total_materials,
        low_stock_materials=low_stock_materials,
        production_batches=production_batches,
        total_production=total_production,
        transactions=transactions,
        materials=materials
    )
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')

        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')

        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')

        else:
            user = User(name=name, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
if __name__ == '__main__':
    print("\nREGISTERED ROUTES:")
    print(app.url_map)

    app.run(debug=True)


