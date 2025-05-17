# E-commerce Admin API - Backend Task

## Features Implemented

*   **Category Management:** Create, Read, Update, Delete product categories.
*   **Product Management:** Create, Read, Update, Delete products, associating them with categories. Includes current stock quantity.
*   **Order Management:** Create new orders (validating stock, updating quantities), Read orders (with filtering by date, product, category, status), Update order status.
*   **Sales & Revenue Analysis:** Endpoint to retrieve aggregated revenue summaries (daily, weekly, monthly, annual) based on completed orders.
*   **Inventory Tracking:** Automatically logs inventory changes due to sales, manual updates, or restocks.
*   **Restock Functionality:** Endpoint to increase product inventory quantities.
*   **Inventory Log Viewing:** Endpoint to view the history of inventory changes for a specific product.
*   **Low Stock Alerts:** Product endpoints indicate if a product's quantity is below a configured threshold.

## Technology Stack

*   **Language:** Python 3.8+
*   **Framework:** FastAPI
*   **Database:** SQLAlchemy ORM with SQLite (for development/testing as implemented here)
*   **Data Validation:** Pydantic
*   **ASGI Server:** Uvicorn

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/HasnainAli47/Forsit-Backend-Developer-Task-Assignment.git
    cd E-commerce-Admin-API
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup:**
    *   **Using SQLite (Current Implementation):** The database file (`./test_database.db`) will be created automatically in the project root directory when the application first runs. No manual database setup is required.

5.  **Run the application:**
    ```bash
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

6.  **Access the API:**
    *   The API will be available at `http://127.0.0.1:8000`.
    * The documentation is available at `http://0.0.0.8000/docs`

## API Endpoints Overview

(Access `/docs` for detailed request/response schemas and testing)

**Categories (`/categories`)**
*   `POST /`: Create a new category.
*   `GET /`: List categories.
*   `GET /{category_id}`: Get a specific category.
*   `PATCH /{category_id}`: Update a category.
*   `DELETE /{category_id}`: Delete a category.

**Products (`/products`)**
*   `POST /`: Create a new product (requires valid `category_id`).
*   `GET /`: List products (includes `is_low_stock` flag). Supports filtering by `category_id` and `low_stock`.
*   `GET /{product_id}`: Get a specific product (includes `is_low_stock` flag).
*   `PATCH /{product_id}`: Update a product (logs inventory changes if quantity is modified).
*   `DELETE /{product_id}`: Delete a product.

**Orders & Sales (`/orders`)**
*   `POST /`: Create a new order (checks stock, updates inventory, creates logs).
*   `GET /`: List orders. Supports filtering by `start_date`, `end_date`, `product_id`, `category_id`, `status`.
*   `GET /{order_id}`: Get a specific order with its items.
*   `PATCH /{order_id}/status`: Update the status of an order.
*   `GET /stats/revenue-summary`: Get revenue summary grouped by `period` (daily, weekly, monthly, annual), supports date filtering.

**Inventory (`/inventory`)**
*   `POST /restock`: Increase inventory for a product and log the event.
*   `GET /logs`: Retrieve inventory change logs for a specific product (`product_id` query parameter required).

**Revenue Summery (`/stats`)**
*   `GET /orders/stats/revenue-summary?period=monthly`: Monthly revenue stats
*   `GET /orders/stats/revenue-summary?period=weekly`: Weekly revenue stats
*   `GET /orders/stats/revenue-summary?period=daily`: daily revenue stats

**Logs of a product (`/logs`)**
*  `GET inventory/logs/?product_id=10` Get logs of product id 10.

## Populating with Demo Data

A script is provided to populate the database with sample categories, products, orders, and inventory events.

**Warning:** By default, the script will **delete all existing data** in the relevant tables before populating. Review the `populate_db.py` script if you wish to disable this behavior.

To run the script: 

1.  Ensure your virtual environment is activated and dependencies are installed.
2.  Make sure the database connection is configured correctly (SQLite file path or MySQL URL).
3.  Run the script from the project root directory:
    ```bash
    python populate_db.py
    ```