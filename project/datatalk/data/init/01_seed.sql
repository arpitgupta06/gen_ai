create table if not exists customers(
    customer_id SERIAL PRIMARY KEY,
    name varchar(100) NOT NULL,
    email varchar(255) UNIQUE,
    city varchar(100),
    region varchar(100),
    signup_date DATE DEFAULT CURRENT_DATE,
    segment varchar(100) DEFAULT 'retail'
        CHECK (segment IN ('retail', 'wholesale', 'premium'))
);

create table if not exists categories (
    category_id SERIAL PRIMARY KEY,
    name varchar(255),
    parent_category varchar(255)
);

create table if not exists products(
    product_id SERIAL PRIMARY KEY,
    name varchar(255),
    category_id int REFERENCES categories(category_id),
    price decimal(10,2),
    cost decimal(10,2),
    sku varchar(100),
    is_active boolean DEFAULT TRUE
);

create table if not exists orders(
    order_id SERIAL PRIMARY KEY,
    customer_id int REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status varchar(100) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'refunded', 'cancelled')),
    shipping_city varchar(100),
    shipping_region varchar(100)
        );

create table if not exists order_items(
    item_id SERIAL PRIMARY KEY,
    order_id int REFERENCES orders(order_id),
    product_id int REFERENCES products(product_id),
    quantity int NOT NULL,
    unit_price decimal(10,2),
    discount decimal(10,2) DEFAULT 0
    );
