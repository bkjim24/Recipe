from flask import Flask, request, jsonify #flask for the api, request for the request and jsonify for the response
import sqlite3 # sqlite for the database
import re # regular expressions for query check
import json #json parsing
import os

#intialize the flask app
app = Flask(__name__)

# Database connection function
def get_db_connection():
    db_path = os.getenv('DB_PATH', 'USA_recipes.db')  # Use environment variable for DB path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def home():
    """Root route that provides information about available API endpoints"""
    return jsonify({
        'status': 'success',
        'message': 'Recipe API is running',
        'available_endpoints': {
            'Get all recipes (paginated)': '/api/recipes?page=1&limit=10',
            'Search recipes': '/api/recipes/search?cuisine=Italian&rating=>4.5',
            'Filter examples': {
                'By calories': '/api/recipes/search?calories=<400',
                'By title': '/api/recipes/search?title=pasta',
                'By cuisine': '/api/recipes/search?cuisine=Italian',
                'By time': '/api/recipes/search?total_time=<30',
                'By rating': '/api/recipes/search?rating=>4.5'
            }
        }
    })

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Fetch paginated recipes sorted by rating"""
    try:
        # Validate and parse query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total count of recipes
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total = cursor.fetchone()[0]

        # Get paginated recipes
        cursor.execute('''
            SELECT id, cuisine, title, rating, prep_time, cook_time, total_time, 
                   description, nutrients, serves 
            FROM recipes 
            ORDER BY rating DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        recipes = []
        for row in cursor.fetchall():
            recipe = dict(row)
            # Safely parse JSON string
            recipe['nutrients'] = json.loads(recipe['nutrients'])
            recipes.append(recipe)

        return jsonify({
            'page': page,
            'limit': limit,
            'total': total,
            'data': recipes
        })
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    except ValueError:
        return jsonify({'error': 'Invalid query parameters'}), 400
    finally:
        conn.close()

@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    """Search recipes based on filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query conditions based on provided filters
        conditions = [] # list to hold query conditions
        params = [] # list to hold query parameters

        # Defines filters and thir database columns
        filters = {
            'calories': r"json_extract(nutrients, '$.calories')",
            'total_time': 'total_time',
            'rating': 'rating'
        }
# Processes numerics filters for calories, total time, and rating
        for key, column in filters.items():
            value = request.args.get(key)
            if value:
                match = re.match(r'([<>=]+)(\d+\.?\d*)', value)
                if match:
                    operator, num_value = match.groups()
                    conditions.append(f"{column} {operator} ?")
                    params.append(num_value)

        # Process title filter (partial match)
        title = request.args.get('title')
        if title:
            conditions.append("title LIKE ?")
            params.append(f'%{title}%')

        # Process cuisine filter
        cuisine = request.args.get('cuisine')
        if cuisine:
            conditions.append("cuisine = ?")
            params.append(cuisine)

        # Build and execute the query
        query = '''
            SELECT id, cuisine, title, rating, prep_time, cook_time, total_time, 
                   description, nutrients, serves 
            FROM recipes
        '''
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        cursor.execute(query, params)

        recipes = []
        for row in cursor.fetchall():
            recipe = dict(row)
            # Safely parse JSON string
            recipe['nutrients'] = json.loads(recipe['nutrients'])
            recipes.append(recipe)
#return filtered recipes in json format
        return jsonify({'data': recipes})
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    except ValueError:
        return jsonify({'error': 'Invalid query parameters'}), 400
    finally:
        conn.close()

# Enable CORS to allow frontend to call this API
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)