import os
import psycopg2
from psycopg2 import sql

def test_pg_connection():
    """
    Connects to the PostgreSQL database, verifies the pgvector extension,
    and performs a basic vector operation.
    """
    conn = None  # Initialize conn to None
    try:
        # Connect to the database using credentials
        # The hostname 'postgres-vector' is the service name from docker-compose
        conn = psycopg2.connect(
            dbname="vector_demo",
            user="postgres",
            password="password",
            host="localhost"
        )
        print("Database connection successful.")

        cursor = conn.cursor()

        # 1. Verify the pgvector extension is enabled
        print("\nChecking for 'vector' extension...")
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        if result:
            print(f"pgvector extension is installed: {result[0]}")
        else:
            print("ERROR: pgvector extension is NOT installed.")
            return

        # 2. Create a test table with a vector column
        print("\nCreating a test table 'items' with a vector column...")
        # Use "DROP TABLE IF EXISTS" for idempotent cleanup before creation
        cursor.execute("DROP TABLE IF EXISTS items;")
        cursor.execute("CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));")
        print("Table 'items' created successfully.")

        # 3. Insert data and perform a similarity search
        print("\nInserting data and performing a similarity search...")
        cursor.execute("INSERT INTO items (embedding) VALUES (%s), (%s), (%s);",
                       ('[1,2,3]', '[4,5,6]', '[1,1,2]'))

        # Perform a cosine distance search
        cursor.execute("SELECT * FROM items ORDER BY embedding <=> '[1,1,1]' LIMIT 1;")
        closest_item = cursor.fetchone()
        print(f"Similarity search complete. Closest vector to [1,1,1] is: {closest_item[1]}")

        # Assert the result is as expected
        if closest_item and closest_item[1] == '[1,1,2]':
            print("Test PASSED: The correct vector was returned.")
        else:
            print("Test FAILED: The returned vector was incorrect.")

    except psycopg2.OperationalError as e:
        print("\nConnection Error: Could not connect to the PostgreSQL server.")
        print("   Make sure the 'postgres-vector' service is running and accessible.")
        print(f"   Error details: {e}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    finally:
        # 4. Clean up and close the connection
        if conn:
            print("\nCleaning up and closing connection...")
            # cursor is only created if conn is successful, so we check it's not closed
            if not conn.closed and not cursor.closed:
                conn.commit()  # Commit any changes (like table creation)
                cursor.close()
            conn.close()
            print("Cleanup complete and connection closed.")

if __name__ == "__main__":
    test_pg_connection()