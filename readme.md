# Python Database Project

This project involves the design and implementation of a database-backed web server for managing customer orders, inventory, and supplier information in a record store. The web server provides full CRUD functionality for interacting with the database and ensures proper data validation, sanitization, and error handling in both local and deployed environments.

## Project Overview

This project aims to create a relational database system that is connected to a Python-based web server. The database stores information about customers, suppliers, records (albums), inventory, and orders, enabling users to perform CRUD operations on the data.

### Key Features

- Full CRUD functionality for interacting with customer orders, inventory, and suppliers
- Proper validation and sanitization of user input
- Error handling to prevent server crashes due to invalid inputs
- Deployment to a publicly-accessible URL, with proper functioning in both local and deployed environments
- A relational database normalized to at least third normal form (3NF)

## Database Design

The database for this project is structured according to the **Entity-Relationship Diagram (ERD)**. The schema is normalized to **third normal form (3NF)** to ensure data integrity and minimize redundancy.

### ERD Overview

The database consists of five tables:

1. **Customers**: Stores customer information.
   - `customer_id`: Primary key, uniquely identifies each customer.
   - `name`, `email`, `phone_number`, `address`: Customer details.

2. **Suppliers**: Stores supplier information.
   - `supplier_id`: Primary key, uniquely identifies each supplier.
   - `name`, `email`, `phone_number`: Supplier details.

3. **Records**: Stores information about records (albums).
   - `record_id`: Primary key, uniquely identifies each record.
   - `title`, `artist`, `price`, `genre`: Details of the record.

4. **Inventory**: Represents the relationship between suppliers and records, including stock quantity and pricing.
   - `inventory_id`: Primary key, uniquely identifies each inventory entry.
   - `supplier_id`: Foreign key referencing `suppliers.supplier_id`.
   - `record_id`: Foreign key referencing `records.record_id`.
   - `stock_quantity`, `price`: Stock details for each record.

5. **Orders**: Represents customer orders, linking customers to the records they purchased.
   - `order_id`: Primary key, uniquely identifies each order.
   - `customer_id`: Foreign key referencing `customers.customer_id`.
   - `record_id`: Foreign key referencing `records.record_id`.
   - `order_date`: The date when the order was placed.

### Database Relationships

- **One-to-Many**: 
  - A customer can place many orders, but each order is linked to one customer.
  - A supplier can provide many records, and each record in inventory is linked to one supplier.
  - A record can appear in many orders, but each order contains one record.

### Database Normalization

The database is normalized to **third normal form (3NF)** to eliminate data redundancy and ensure optimal data integrity. This involves:

1. Ensuring that each table contains only related data.
2. Removing partial and transitive dependencies.
3. Ensuring non-key attributes depend on the primary key.

## Web Server

The web server is built using Python and interacts with the PostgreSQL database. It provides RESTful APIs that allow users to create, read, update, and delete records, customers, orders, and inventory.

### Features of the Web Server

- **CRUD Operations**: The web server provides the ability to create, read, update, and delete records in the database via HTTP requests.
- **Data Validation & Sanitization**: All user input is properly validated and sanitized to prevent SQL injection and other vulnerabilities.
- **Error Handling**: The server handles errors gracefully, returning appropriate error messages without crashing.
- **Deployment**: The server is deployed to a publicly-accessible URL and functions both locally and in a deployed environment.

## Design Decisions

### Feedback and Response

During the planning stage, I sought feedback from two peers. Their input included suggestions for optimizing the database schema and ensuring the web server followed best practices for handling errors and validating inputs. Based on this feedback:

- I simplified some relationships in the database to improve query efficiency.
- I incorporated more robust error handling in the web server to improve stability and user experience.

### Justification

These changes were made to ensure that the system performs efficiently, maintains data integrity, and provides a user-friendly experience by handling unexpected errors smoothly.

## Installation

To set up and run the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Coderaccangus/recordstoredb
   cd your-repository

2. Set up a virtual environment:
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install the dependencies from requirements.txt:
    pip install -r requirements.txt

4. Flask Commands
    flask create: This command initializes the database by creating the tables defined in the models. It ensures that the database schema is set up before any data can be added.

    flask seed: This command populates the database with initial data, such as sample records, customers, and suppliers. This is useful for testing or setting up default values in the system.

    flask run: This starts the Flask development server. By default, the server will be hosted at http://localhost:5000, where you can interact with the API and access the web application

    The server will be accessible at http://localhost:5000 (or a different port, depending on configuration). In addition, the project is deployed and hosted at https://recordstoredb.onrender.com/.