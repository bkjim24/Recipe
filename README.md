#Overview
This project implements an application that parses recipe data from the JSON file, stores it in a SQlite database, and provides an API to access and search the data. This assessment also includes a frontend UI that gathers from the API to display the recipe information with filtering, sorting, and pagination capabilities.

# Backend
- Data Parsing: Reads and parses recipe data from the JSON file called USA_recipes.json
- Data storing: Stores the parsed data in a sqlite database
-API: /api/recipes: fetches all recipes with pagination and sorting.
-/api/recipes/search: searches recipes by title, cuisine, rating, and total time.

#frontend
-Recipe table: Displays the recipes with columns for Title, Cuisine, Rating, Total Time, and serves.
-Filters each columns to refine search results.
 - Responsive recipe table with filtering capabilities
  - Detailed recipe view in a side drawer
  - Pagination controls with customizable results per page
  - Star rating visualization
  - Expandable details for time information
  - Nutrition information table



# Setup and Installation
## Prerequisites
-Python 3.7, I used VSCODE and installed python through there.		
-Flask -> Installed in vscode terminal ‘pip install flask’or if on mac 'pip3 install flask'
-Download SQlite extension in vscode
-Download liveserver extension in vscode
### Installation
1.	Get clone Repository 
2.	I used vscode to run this project.
3.	Install Flask in vscode terminal ‘pip install flask’
4.	Get vscode extensions liveserver and sqlite
5.	Run ‘python recipes_storingrecipe.py’ to create a database called USA_recipes.db
6.	Ctrl-c and then run ‘python runningtheapi.py’ to run the API to the server.
7.	Then right click on recipeapp.html and click on ‘Open with live server’
8. Should open the server and the site for recipes :) have fun
