import sqlite3  # SQLite library for the data
import json  # JSON library for parsing the JSON data
from flask import Flask, request, jsonify  # Flask Framework for the API
import re  # Regular expressions for query validation

# Initialize Flask app
app = Flask(__name__)

# Connect to SQLite database
# Allows multiple threads to access the database
conn = sqlite3.connect('USA_recipes.db', check_same_thread=False)
cursor = conn.cursor()

# Create table with specified fields if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cuisine VARCHAR,
    title VARCHAR,
    rating FLOAT,
    prep_time INT,
    cook_time INT,
    total_time INT,
    description TEXT,
    nutrients TEXT,
    serves VARCHAR
)
''')

# Read and parse JSON file
with open('USA_recipes.json', 'r', encoding='utf-8') as file:
    content = file.read()
    try:
        # Parse the JSON content
        recipes = json.loads(content)
        # If the JSON is a dictionary with keys, convert it to a list
        if isinstance(recipes, dict):  # Handle dictionary with numeric keys
            recipes = list(recipes.values())
    except json.JSONDecodeError:
        recipes = [json.loads(line) for line in content.splitlines() if line.strip()]

print(f"Found {len(recipes)} recipes to import")

# Insert data into the SQLite database
for i, recipe in enumerate(recipes):
    try:
        cursor.execute('''
        INSERT INTO recipes (cuisine, title, rating, prep_time, cook_time, total_time, description, nutrients, serves)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe.get('cuisine'),
            recipe.get('title'),
            None if recipe.get('rating') in ['NaN', None] else float(recipe.get('rating')),
            None if recipe.get('prep_time') in ['NaN', None] else int(recipe.get('prep_time')),
            None if recipe.get('cook_time') in ['NaN', None] else int(recipe.get('cook_time')),
            None if recipe.get('total_time') in ['NaN', None] else int(recipe.get('total_time')),
            recipe.get('description'),
            json.dumps(recipe.get('nutrients', {})),  # Convert nutrients to JSON string
            recipe.get('serves')
        ))

        # Print progress every 100 recipes
        if (i + 1) % 100 == 0:
            print(f"Imported {i + 1} recipes so far")

    except Exception as e:
        print(f"Error processing recipe {i}: {e}")
        print(f"Recipe data: {recipe}")

# Commit the changes to the database
conn.commit()
print("Database created and populated successfully!")

# Flask API Endpoints

# Endpoint 1: Get all recipes (paginated and sorted by rating)
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    # Query to get the recipes sorted by rating in descending order
    cursor.execute('''
    SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves
    FROM recipes
    ORDER BY rating DESC
    LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()

    # Get the total number of recipes in the DB
    total_count = cursor.execute('SELECT COUNT(*) FROM recipes').fetchone()[0]

    # Convert the results into a list of dictionaries
    recipes = []
    for row in rows:
        recipes.append({
            "id": row[0],
            "title": row[1],
            "cuisine": row[2],
            "rating": row[3],
            "prep_time": row[4],
            "cook_time": row[5],
            "total_time": row[6],
            "description": row[7],
            "nutrients": json.loads(row[8]),
            "serves": row[9]
        })

    # Return the paginated results in JSON response
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total_count,
        "data": recipes
    })

# Endpoint 2: Search recipes
@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    """
    Search recipes based on filters.
    """
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        # Get search parameters
        title = request.args.get('title', '')
        cuisine = request.args.get('cuisine', '')
        filters = {
            'rating': request.args.get('rating', ''),
            'total_time': request.args.get('total_time', '')
        }

        # Debugging: Log the received parameters
        print(f"Search parameters - Title: {title}, Cuisine: {cuisine}, Filters: {filters}")

        # Base query
        query = '''
        SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves
        FROM recipes
        WHERE 1=1
        '''
        params = []

        # Add filters to the query
        if title:
            query += ' AND title LIKE ?'
            params.append(f'%{title}%')
        if cuisine:
            query += ' AND cuisine LIKE ?'
            params.append(f'%{cuisine}%')

        # Dynamically handle numeric filters (rating, total_time)
        for key, value in filters.items():
            if value:
                match = re.match(r'([<>=]+)(\d+\.?\d*)', value)
                if match:
                    operator, num_value = match.groups()
                    query += f' AND {key} {operator} ?'
                    params.append(float(num_value) if '.' in num_value else int(num_value))

        # Get total count of filtered recipes
        count_query = f'SELECT COUNT(*) FROM ({query})'
        total_count = cursor.execute(count_query, params).fetchone()[0]

        # Add pagination to the query
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        # Execute the query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert rows to dictionaries
        recipes = []
        for row in rows:
            recipes.append({
                "id": row[0],
                "title": row[1],
                "cuisine": row[2],
                "rating": row[3],
                "prep_time": row[4],
                "cook_time": row[5],
                "total_time": row[6],
                "description": row[7],
                "nutrients": json.loads(row[8]),
                "serves": row[9]
            })

        # Return the response
        return jsonify({
            "page": page,
            "limit": limit,
            "total": total_count,
            "data": recipes
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Error in search_recipes: {e}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
