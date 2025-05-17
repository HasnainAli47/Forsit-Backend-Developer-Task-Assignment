import random
import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

# --- Database Setup ---
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderStatusEnum
from app.models.order_item import OrderItem
from app.models.inventory_log import InventoryLog, InventoryLogReasonEnum

# Import Schemas
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate
from app.schemas.order import OrderCreate
from app.schemas.order_item import OrderItemCreate
from app.schemas.inventory_log import RestockCreate

from app.crud import crud_category, crud_product, crud_order, crud_inventory

print("--- Starting Database Population Script ---")

SAMPLE_CATEGORIES = [
    {"name": "Electronics", "description": "Gadgets, devices, and accessories"},
    {"name": "Apparel", "description": "Clothing, shoes, and fashion items"},
    {"name": "Home & Kitchen", "description": "Appliances, cookware, and home goods"},
    {"name": "Books", "description": "Fiction, non-fiction, educational books"},
    {"name": "Toys & Games", "description": "Fun and games for all ages"},
]

SAMPLE_PRODUCTS = {
    "Electronics": [
        {"name": "Smart Echo Speaker", "description": "Voice-controlled smart speaker", "price": 49.99, "initial_quantity": 75},
        {"name": "Noise-Cancelling Headphones", "description": "Wireless over-ear headphones", "price": 199.00, "initial_quantity": 40},
        {"name": "4K Streaming Stick", "description": "Stream movies and TV in 4K", "price": 39.99, "initial_quantity": 150},
        {"name": "Gaming Mouse", "description": "High-precision RGB gaming mouse", "price": 59.99, "initial_quantity": 60},
    ],
    "Apparel": [
        {"name": "Men's Cotton T-Shirt", "description": "Basic crew neck t-shirt", "price": 15.00, "initial_quantity": 200},
        {"name": "Women's Skinny Jeans", "description": "Stretch denim skinny jeans", "price": 45.50, "initial_quantity": 80},
        {"name": "Unisex Running Shoes", "description": "Lightweight athletic shoes", "price": 79.95, "initial_quantity": 50},
    ],
    "Home & Kitchen": [
        {"name": "Drip Coffee Maker", "description": "12-cup programmable coffee maker", "price": 35.00, "initial_quantity": 90},
        {"name": "Digital Air Fryer", "description": "5.8 Quart capacity air fryer", "price": 89.99, "initial_quantity": 30},
        {"name": "Robot Vacuum Cleaner", "description": "Self-charging robotic vacuum", "price": 249.99, "initial_quantity": 15},
    ],
    "Books": [
        {"name": "The Sci-Fi Chronicle", "description": "A thrilling space opera novel", "price": 14.99, "initial_quantity": 120},
        {"name": "Advanced Python Programming", "description": "In-depth Python guide", "price": 55.00, "initial_quantity": 55},
    ],
    "Toys & Games": [
        {"name": "1000 Piece Jigsaw Puzzle", "description": "Challenging landscape puzzle", "price": 19.95, "initial_quantity": 100},
        {"name": "Remote Control Car", "description": "Fast RC car for kids", "price": 29.99, "initial_quantity": 70},
    ]
}

def populate(db: Session):
    """Populates the database with sample data."""
    print("WARNING: Clearing existing data...")
    db.query(InventoryLog).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.commit()
    print("Existing data cleared.")

    print("Creating categories...")
    created_categories = {}
    for cat_data in SAMPLE_CATEGORIES:
        cat_schema = CategoryCreate(**cat_data)
        category = crud_category.create_category(db=db, category=cat_schema)
        created_categories[category.name] = category
        print(f"  Created Category: {category.name}")
    print("Categories created.")

    print("Creating products and initial stock logs...")
    created_products = []
    for cat_name, products_list in SAMPLE_PRODUCTS.items():
        category = created_categories[cat_name]
        for prod_data_original in products_list:
            prod_data = prod_data_original.copy()
            initial_qty = prod_data.pop("initial_quantity")

            prod_schema = ProductCreate(**prod_data, category_id=category.id, quantity=0)
            product = crud_product.create_product(db=db, product=prod_schema)

            if product:
                 product.quantity = initial_qty
                 db.add(product)
                 db.commit()
                 db.refresh(product)

                 crud_inventory.create_inventory_log(
                     db=db,
                     product_id=product.id,
                     change_amount=initial_qty, # The change *is* the initial quantity
                     reason=InventoryLogReasonEnum.INITIAL_STOCK,
                     notes="Initial stock population"
                 )
                 db.commit()

                 created_products.append(product)
                 print(f"  Created Product: {product.name} (Qty: {product.quantity}) in Category: {category.name}")
            else:
                 print(f"  ERROR Creating Product: {prod_data['name']}")

    print("Products and initial stock logs created.")


    print("Simulating orders...")
    if not created_products:
        print("No products available to create orders. Skipping.")
        return

    num_orders_to_create = 30
    for i in range(num_orders_to_create):
        print(f"  Creating Order {i+1}/{num_orders_to_create}...")
        order_items_data = []
        num_items_in_order = random.randint(1, 4)
        potential_products = random.sample(created_products, min(len(created_products), num_items_in_order * 2)) # Get some candidates

        products_in_this_order = set()
        for product in potential_products:
            if len(order_items_data) >= num_items_in_order:
                break
            if product.id in products_in_this_order:
                continue
            if product.quantity > 0:
                order_qty = random.randint(1, min(3, product.quantity))
                order_items_data.append(OrderItemCreate(
                    product_id=product.id,
                    quantity=order_qty,
                ))
                products_in_this_order.add(product.id)

        if not order_items_data:
             print(f" Could not add items to order {i+1} (likely stock issues). Skipping.")
             continue

        status_choice = random.choices(
            [OrderStatusEnum.COMPLETED, OrderStatusEnum.PENDING, OrderStatusEnum.CANCELLED],
            weights=[80, 15, 5],
            k=1
        )[0]

        order_schema = OrderCreate(items=order_items_data, status=status_choice)

        created_order, error_message = crud_order.create_order(db=db, order_in=order_schema)

        if created_order:
            order_date_delta = datetime.timedelta(days=random.randint(1, 60))
            created_order.order_date = datetime.datetime.now(datetime.timezone.utc) - order_date_delta
            db.commit()
            print(f" Created Order ID: {created_order.id}, Status: {created_order.status.value}, Date: {created_order.order_date.date()}")
        else:
            print(f"    ERROR Creating Order {i+1}: {error_message}")

    print("Order simulation finished.")


    print("Simulating restocks...")
    num_restocks = 5
    for _ in range(num_restocks):
         product_to_restock = random.choice(created_products)
         qty_added = random.randint(10, 50)
         restock_schema = RestockCreate(product_id=product_to_restock.id, quantity_added=qty_added, notes="Scheduled restock")
         updated_prod, log, err = crud_inventory.restock_product(db=db, restock_info=restock_schema)
         if updated_prod:
             print(f"  Restocked Product ID: {updated_prod.id} ({updated_prod.name}) by {qty_added}. New Qty: {updated_prod.quantity}")
         else:
             print(f"  ERROR Restocking Product ID {product_to_restock.id}: {err}")
    print("Restock simulation finished.")


if __name__ == "__main__":
    print("Attempting to connect to database...")
    db: Session = SessionLocal()
    try:
        print("Database connection successful.")
        populate(db)
        print("--- Database Population Script Finished Successfully-")
    except Exception as e:
        print("\n--- ERROR DURING DATABASE POPULATION ---")
        print(f"An error occurred: {e}")
        print("-----------------------------")
    finally:
        print("Closing database session.")
        db.close()

if __name__ == "__main__":
    print("Attempting to connect to database...")
    db: Session = SessionLocal()

    try:
        print("Ensuring database tables exist...")
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created.")

        print("Database connection successful.") 
        populate(db)
        print("Database Population Script Finished Successfully")
    except Exception as e:
        print("\nERROR DURING DATABASE POPULATION")
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("-----------------------")
    finally:
        print("Closing database session.")
        db.close()