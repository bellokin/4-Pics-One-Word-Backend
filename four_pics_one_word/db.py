import psycopg2
from psycopg2 import sql

def create_connection():
    """Function to create a connection to the PostgreSQL database."""
    try:
        # Your database connection string
        conn = psycopg2.connect(
            "postgres://avnadmin:AVNS_w_oq28x8DeQqvsPPX6q@pg-de49627-bellokingdavidibukun03-8a91.e.aivencloud.com:23673/defaultdb?sslmode=require"
        )
        return conn
    except Exception as e:
        print(f"Error: Unable to connect to the database\n{e}")
        return None


def execute_query(conn, query_sql, params=None):
    """Function to execute a query on the database, optionally with parameters."""
    try:
        # Create a cursor
        cur = conn.cursor()

        # Execute the query with parameters if provided
        cur.execute(query_sql, params)

        # Fetch the result of the query
        result = cur.fetchone()

        # Close the cursor
        cur.close()

        # Return the result
        return result
    except Exception as e:
        print(f"Error: Unable to execute query\n{e}")
        return None


def main():
    """Main function to connect to the database and execute a query."""
    # Establish connection
    conn = create_connection()
    if conn is not None:
        # Define the SQL query and parameters (as an example)
        query_sql = 'SELECT VERSION()'
        params = None  # No parameters for this query, can be updated dynamically for other queries

        # Execute the query and fetch the result
        result = execute_query(conn, query_sql, params)

        if result:
            # Print the result
            print(f"Database version: {result[0]}")

        # Close the connection
        conn.close()
        print("Connection closed successfully.")


if __name__ == "__main__":
    main()
