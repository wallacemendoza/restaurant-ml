import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# DATA SOURCE SWITCHER
# To connect your real PostgreSQL database, set USE_REAL_DB = True
# and fill in your DATABASE_URL below.
# Everything else stays the same.
# ─────────────────────────────────────────────────────────────
USE_REAL_DB  = False
DATABASE_URL = "postgresql://postgres:yourpassword@localhost/restaurant_db"

def load_from_postgres():
    """Load real data from restaurant_db PostgreSQL instance."""
    import psycopg2
    import psycopg2.extras

    conn = psycopg2.connect(DATABASE_URL)

    # Orders
    df_orders = pd.read_sql("""
        SELECT o.id, o.created_at, o.status,
               rt.number AS table_number, rt.location,
               CONCAT(c.first_name, ' ', c.last_name) AS customer_name
        FROM orders o
        LEFT JOIN restaurant_tables rt ON rt.id = o.table_id
        LEFT JOIN customers c ON c.id = o.customer_id
        WHERE o.status = 'delivered'
    """, conn)

    # Order items with menu info
    df_items = pd.read_sql("""
        SELECT oi.order_id, oi.quantity, oi.unit_price,
               oi.quantity * oi.unit_price AS line_total,
               mi.id AS menu_item_id, mi.name AS item_name,
               mi.price, mi.cost, mi.category_id,
               cat.name AS category,
               rt.location
        FROM order_items oi
        JOIN orders o         ON o.id = oi.order_id AND o.status = 'delivered'
        JOIN menu_items mi    ON mi.id = oi.menu_item_id
        JOIN categories cat   ON cat.id = mi.category_id
        JOIN restaurant_tables rt ON rt.id = o.table_id
        WHERE NOT oi.is_voided
    """, conn)

    # Menu reference
    df_menu = pd.read_sql("""
        SELECT mi.id, mi.name, mi.price, mi.cost,
               cat.name AS category
        FROM menu_items mi
        JOIN categories cat ON cat.id = mi.category_id
        WHERE mi.is_available = TRUE
    """, conn)

    conn.close()
    return df_orders, df_items, df_menu


def load_mock_data():
    """
    Generate mock data that exactly mirrors restaurant_db schema.
    Same column names and types as the PostgreSQL queries above.
    """
    np.random.seed(42)
    random.seed(42)

    # ── Menu (mirrors menu_items + categories) ────────────────
    menu_raw = [
        # (id, name, category, price, cost)
        (1,  "Garlic Bread",         "Starters",  6.50,  1.80),
        (2,  "Chicken Wings",        "Starters", 14.00,  4.50),
        (3,  "Bruschetta",           "Starters",  9.00,  2.50),
        (4,  "Calamari",             "Starters", 13.00,  4.20),
        (5,  "Spring Rolls",         "Starters",  8.00,  2.20),
        (6,  "Tomato Bisque",        "Soups",     8.00,  1.90),
        (7,  "French Onion Soup",    "Soups",    10.00,  2.80),
        (8,  "Caesar Salad",         "Salads",   12.00,  3.20),
        (9,  "Greek Salad",          "Salads",   11.00,  2.80),
        (10, "Chicken & Avocado",    "Salads",   15.00,  4.80),
        (11, "Grilled Salmon",       "Mains",    26.00,  9.50),
        (12, "Beef Tenderloin",      "Mains",    38.00, 15.00),
        (13, "Chicken Parmesan",     "Mains",    22.00,  7.20),
        (14, "Mushroom Risotto",     "Mains",    20.00,  5.80),
        (15, "Fish & Chips",         "Mains",    21.00,  6.90),
        (16, "Classic Smash",        "Burgers",  17.00,  5.50),
        (17, "BBQ Bacon Burger",     "Burgers",  19.00,  6.20),
        (18, "Veggie Burger",        "Burgers",  16.00,  4.80),
        (19, "Carbonara",            "Pasta",    18.00,  5.20),
        (20, "Penne Arrabbiata",     "Pasta",    15.00,  3.60),
        (21, "Seafood Linguine",     "Pasta",    28.00, 10.50),
        (22, "Margherita",           "Pizza",    16.00,  4.20),
        (23, "Pepperoni",            "Pizza",    19.00,  5.50),
        (24, "Truffle Bianca",       "Pizza",    22.00,  6.80),
        (25, "Tiramisu",             "Desserts",  9.00,  2.80),
        (26, "Chocolate Lava Cake",  "Desserts", 11.00,  3.20),
        (27, "Crème Brûlée",         "Desserts",  9.00,  2.50),
        (28, "Gelato",               "Desserts",  8.00,  2.00),
        (29, "Soft Drink",           "Drinks",    4.00,  0.60),
        (30, "Fresh Juice",          "Drinks",    6.00,  1.20),
        (31, "House Wine",           "Drinks",    9.00,  2.50),
        (32, "Craft Beer",           "Drinks",    8.00,  2.20),
        (33, "Espresso",             "Drinks",    4.00,  0.50),
        (34, "Kids Pasta",           "Kids Menu", 9.00,  2.20),
        (35, "Kids Chicken Nuggets", "Kids Menu",10.00,  3.00),
        (36, "Kids Ice Cream",       "Kids Menu", 5.00,  1.20),
    ]
    df_menu = pd.DataFrame(menu_raw, columns=["id","name","category","price","cost"])

    # ── Orders (mirrors orders + restaurant_tables + customers) ─
    locations = ["indoor", "patio", "bar", "private"]
    location_weights = [0.55, 0.25, 0.12, 0.08]

    n_orders = 180
    start_date = datetime.now() - timedelta(days=90)
    order_rows = []
    for i in range(1, n_orders + 1):
        day_offset = np.random.randint(0, 90)
        hour = np.random.choice(
            [11,12,13,14,19,20,21,22],
            p=[0.05,0.12,0.14,0.08,0.10,0.20,0.22,0.09]
        )
        created_at = start_date + timedelta(days=day_offset, hours=hour,
                                            minutes=random.randint(0,59))
        order_rows.append({
            "id": i,
            "created_at": created_at,
            "status": "delivered",
            "table_number": f"T{random.randint(1,13):02d}",
            "location": np.random.choice(locations, p=location_weights),
            "customer_name": random.choice([
                "Lucas Oliveira","Fernanda Costa","Rafael Santos",
                "Ana Lima","Bruno Ferreira","Camila Rodrigues",
                "Diego Souza","Isabela Mendes","Carlos Pereira","Sofia Alves"
            ])
        })
    df_orders = pd.DataFrame(order_rows)

    # ── Order items (mirrors order_items + menu_items + categories) ─
    # Simulate realistic popularity weights
    popularity = np.array([
        2, 4, 3, 3, 2,   # Starters
        2, 2,             # Soups
        3, 2, 3,          # Salads
        5, 3, 5, 4, 4,   # Mains
        6, 5, 3,          # Burgers
        4, 3, 3,          # Pasta
        5, 6, 4,          # Pizza
        4, 3, 2, 3,       # Desserts
        6, 4, 5, 4, 3,   # Drinks
        2, 2, 2            # Kids
    ], dtype=float)
    popularity /= popularity.sum()

    item_rows = []
    for order in order_rows:
        n_items = np.random.randint(1, 5)
        chosen_ids = np.random.choice(
            df_menu["id"].values, size=n_items,
            replace=False, p=popularity[:len(df_menu)]
        )
        for mid in chosen_ids:
            row = df_menu[df_menu["id"] == mid].iloc[0]
            qty = np.random.choice([1,2,3], p=[0.70,0.22,0.08])
            item_rows.append({
                "order_id":     order["id"],
                "menu_item_id": int(mid),
                "item_name":    row["name"],
                "category":     row["category"],
                "price":        row["price"],
                "cost":         row["cost"],
                "quantity":     qty,
                "unit_price":   row["price"],
                "line_total":   row["price"] * qty,
                "location":     order["location"],
            })

    df_items = pd.DataFrame(item_rows)
    return df_orders, df_items, df_menu


# ─── PUBLIC ENTRYPOINT ────────────────────────────────────────
def load_data():
    """
    Returns (df_orders, df_items, df_menu).
    Swap USE_REAL_DB = True at the top to connect your PostgreSQL.
    """
    if USE_REAL_DB:
        return load_from_postgres()
    return load_mock_data()
