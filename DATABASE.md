## Database Schema Documentation

This document outlines the database schema for the E-commerce Admin API.

---

### Table: `categories`

*   **Purpose:** Stores product category information.
*   **Columns:**
    *   `id` (Integer, Primary Key, Indexed): Unique identifier for the category.
    *   `name` (String(100), Unique, Indexed, Not Null): Name of the category.
    *   `description` (Text, Nullable): description of the category.
*   **Relationships:**
    *   One-to-Many with `products` (one category has many products).

---

### Table: `products`

*   **Purpose:** Stores information about individual products.
*   **Columns:**
    *   `id` (Integer, Primary Key, Indexed): Unique identifier for the product.
    *   `name` (String(100), Indexed, Not Null): Name of the product.
    *   `description` (Text, Nullable): description of the product.
    *   `price` (Float, Not Null): Current selling price of the product.
    *   `quantity` (Integer, Not Null, Default: 0): Current stock level (quantity on hand).
    *   `category_id` (Integer, Foreign Key -> `categories.id`, Not Null): Links the product to its category.
    *   `created_at` (DateTime(timezone=True), Not Null, Default: current time): Timestamp of product creation.
    *   `updated_at` (DateTime(timezone=True), Not Null, Default/OnUpdate: current time): Timestamp of last product update.
*   **Relationships:**
    *   Many-to-One with `categories` (many products belong to one category).
    *   One-to-Many with `order_items` (one product can be in many order items).
    *   One-to-Many with `inventory_logs` (one product has many inventory log entries).

---

### Table: `orders`

*   **Purpose:** Stores information about customer orders.
*   **Columns:**
    *   `id` (Integer, Primary Key, Indexed): Unique identifier for the order.
    *   `order_date` (DateTime(timezone=True), Indexed, Not Null, Default: current time): Timestamp when the order was placed.
    *   `total_amount` (Float, Not Null): Total calculated amount for the order.
    *   `status` (Enum(OrderStatusEnum), Indexed, Not Null, Default: 'pending'): Current status of the order ('pending', 'completed', 'cancelled').
    *   `created_at` (DateTime(timezone=True), Not Null, Default: current time): Timestamp of order record creation.
    *   `updated_at` (DateTime(timezone=True), Not Null, Default/OnUpdate: current time): Timestamp of last order update.
*   **Relationships:**
    *   One-to-Many with `order_items` (one order contains many items). Items are deleted if the order is deleted (cascade).
    *   One-to-Many with `inventory_logs` (one order can be associated with multiple inventory log entries, via `order_id` in logs).

---

### Table: `order_items`

*   **Purpose:** Stores details about individual items within an order (line items). Represents the link between orders and products for a specific sale.
*   **Columns:**
    *   `id` (Integer, Primary Key, Indexed): Unique identifier for the order item line.
    *   `quantity` (Integer, Not Null): Quantity of the product purchased in this line item.
    *   `price_per_unit` (Float, Not Null): Price of the product at the time the order was placed*.
    *   `order_id` (Integer, Foreign Key -> `orders.id`, Not Null): Links the item to its order.
    *   `product_id` (Integer, Foreign Key -> `products.id`, Not Null): Links the item to the specific product purchased.
*   **Relationships:**
    *   Many-to-One with `orders` (many items belong to one order).
    *   Many-to-One with `products` (many order items can refer to the same product).

---

### Table: `inventory_logs`

*   **Purpose:** Tracks changes to product inventory levels over time for auditing.
*   **Columns:**
    *   `id` (Integer, Primary Key, Indexed): Unique identifier for the log entry.
    *   `timestamp` (DateTime(timezone=True), Indexed, Not Null, Default: current time): Timestamp when the inventory change occurred.
    *   `change_amount` (Integer, Not Null): The amount the quantity changed (+ve for increase, -ve for decrease).
    *   `new_quantity` (Integer, Not Null): The resulting product quantity after the change.
    *   `reason` (Enum(InventoryLogReasonEnum), Indexed, Not Null): Reason for the change ('sale', 'restock', 'manual_update', etc.).
    *   `notes` (String(255), Nullable): Optional notes regarding the change.
    *   `product_id` (Integer, Foreign Key -> `products.id`, Indexed, Not Null): Links the log entry to the affected product.
    *   `order_id` (Integer, Foreign Key -> `orders.id`, Indexed, Nullable): Links the log entry to an order if the change was due to a 'sale' or 'return'.
*   **Relationships:**
    *   Many-to-One with `products` (many log entries can belong to one product).
    *   Many-to-One with `orders` (many log entries can optionally belong to one order).

---