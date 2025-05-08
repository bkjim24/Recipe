# Recipe# Recipe API and Frontend Application

## Overview
This project implements a full-stack application that parses recipe data from a JSON file, stores it in a SQLite database, and provides a RESTful API to access and search the data. The project also includes a frontend UI that consumes this API to display recipe information with filtering, sorting, and pagination capabilities.

## Project Structure

## Features
- **Data Storage**: JSON recipe data parsing and storage in SQLite database
- **RESTful API**: Backend API with pagination, sorting, and filtering capabilities
- **Frontend UI**:
  - Responsive recipe table with filtering capabilities
  - Detailed recipe view in a side drawer
  - Pagination controls with customizable results per page
  - Star rating visualization
  - Expandable details for time information
  - Nutrition information table

## Setup and Installation

### Prerequisites
- Python 3.7+
- Flask
- SQLite3

### Installation Steps
1. Clone or download the repository
2. Install required Python packages: update, flask, sqlite    
3. Set up the database:
  1. run in terminal python storing_recipes.py and should create a USA_recipes.db from USA_recipes.json
  2. run in terminal python runningtheapi.py and should start the local server. MUST INSTALL FLASK, SQLITE, AND LIVESERVER FROM VSCODE TO WORK
  3. Right click on recipeapp.html and *open with liveserver*
