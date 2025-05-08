import sqlite3  # SQLite library for the data 
import json # JSON library for parsing the JSON data
from flask import Flask, request, jsonify #FLask Framework for the API

# Initialize Flask app
app = Flask(__name__)

# Connect to SQLite database
# Allows mutlitple threads to access the database
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
        #Parse the JSON content
        recipes = json.loads(content)
        #IF the JSOn is a dictionary with keys, covert it to a list
        if isinstance(recipes, dict):  # Handle dictionary with numeric keys
            recipes = list(recipes.values())
    except json.JSONDecodeError:
        recipes = [json.loads(line) for line in content.splitlines() if line.strip()]

print(f"Found {len(recipes)} recipes to import")

# Insert data into the SQlite database
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
#commits the changes to the database
conn.commit()
print("Database created and populated successfully!")

# Flask API Endpoints

# Endpoint 1: Get all recipes (paginated and sorted by rating)
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
# Query to get the recipes sorted by rating in descinding order
    cursor.execute('''
    SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves
    FROM recipes
    ORDER BY rating DESC
    LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
# Gets the total number of recipes in the DB
    total_count = cursor.execute('SELECT COUNT(*) FROM recipes').fetchone()[0]
# Converts the results into a list of dictionaries
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
# Returns the paginated results in JSON response
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total_count,
        "data": recipes
    })

# Endpoint 2: Search recipes
@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    # Gets search paramters from the request
    title = request.args.get('title', '') # search by title
    cuisine = request.args.get('cuisine', '') # search by cuisine
    rating = request.args.get('rating', '') # search by rating
    total_time = request.args.get('total_time', '') # search by total time
# base query to get the recipes
    query = '''
    SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves
    FROM recipes
    WHERE 1=1
    '''
    params = []
# add filters to the query based on the provided parameters
    if title:
        query += ' AND title LIKE ?'
        params.append(f'%{title}%')
    if cuisine:
        query += ' AND cuisine LIKE ?'
        params.append(f'%{cuisine}%')
    if rating:
        query += ' AND rating >= ?'
        params.append(float(rating))
    if total_time:
        query += ' AND total_time <= ?'
        params.append(int(total_time))

    cursor.execute(query, params)
    rows = cursor.fetchall()

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

    return jsonify({"data": recipes})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)