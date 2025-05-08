const API_BASE_URL = "http://127.0.0.1:5000/api/recipes"; // Update with your API URL

// DOM Elements
const recipeTableBody = document.getElementById("recipe-table-body");
const noResultsMessage = document.getElementById("no-results-message");
const noDataMessage = document.getElementById("no-data-message");
const prevPageButton = document.getElementById("prev-page");
const nextPageButton = document.getElementById("next-page");
const pageInfo = document.getElementById("page-info");
const perPageSelect = document.getElementById("per-page-select");
const filterTitle = document.getElementById("filter-title");
const filterCuisine = document.getElementById("filter-cuisine");
const filterRating = document.getElementById("filter-rating");
const filterTime = document.getElementById("filter-time");
const filterServes = document.getElementById("filter-serves");
const drawer = document.getElementById("recipe-drawer");
const overlay = document.getElementById("overlay");
const drawerCloseButton = document.getElementById("drawer-close");

// Drawer Elements
const drawerTitle = document.getElementById("drawer-title");
const recipeDescription = document.getElementById("recipe-description");
const recipeTotalTime = document.getElementById("recipe-total-time");
const recipePrepTime = document.getElementById("recipe-prep-time");
const recipeCookTime = document.getElementById("recipe-cook-time");
const recipeServes = document.getElementById("recipe-serves");
const nutritionTableBody = document.getElementById("nutrition-table-body");

// Pagination and Filters
let currentPage = 1;
let resultsPerPage = 15;
let filters = {};

// Fetch Recipes from API
async function fetchRecipes() {
    const params = new URLSearchParams({
        page: currentPage,
        limit: resultsPerPage,
        title: filters.title || "",
        cuisine: filters.cuisine || "",
        rating: filters.rating || "",
        total_time: filters.total_time || "",
        serves: filters.serves || ""
    });

    try {
        const response = await fetch(`${API_BASE_URL}/search?${params.toString()}`);
        const data = await response.json();

        renderRecipes(data.data);
        updatePagination(data.page, Math.ceil(data.total / resultsPerPage));
    } catch (error) {
        console.error("Error fetching recipes:", error);
        showNoDataMessage();
    }
}

// Render Recipes in Table
function renderRecipes(recipes) {
    recipeTableBody.innerHTML = "";

    if (recipes.length === 0) {
        showNoResultsMessage();
        return;
    }

    hideMessages();

    recipes.forEach((recipe) => {
        const row = document.createElement("tr");
        row.classList.add("recipe-row");
        row.dataset.recipe = JSON.stringify(recipe);

        row.innerHTML = `
            <td title="${recipe.title}">${truncateText(recipe.title, 20)}</td>
            <td>${recipe.cuisine || "N/A"}</td>
            <td>${renderStars(recipe.rating)}</td>
            <td>${recipe.total_time ? `${recipe.total_time} mins` : "N/A"}</td>
            <td>${recipe.serves || "N/A"}</td>
        `;

        row.addEventListener("click", () => openDrawer(recipe));
        recipeTableBody.appendChild(row);
    });
}

// Update Pagination Controls
function updatePagination(current, totalPages) {
    pageInfo.textContent = `Page ${current} of ${totalPages}`;
    prevPageButton.disabled = current === 1;
    nextPageButton.disabled = current === totalPages;
}

// Open Drawer with Recipe Details
function openDrawer(recipe) {
    drawerTitle.textContent = `${recipe.title} (${recipe.cuisine || "N/A"})`;
    recipeDescription.textContent = recipe.description || "No description available.";
    recipeTotalTime.textContent = recipe.total_time ? `${recipe.total_time} mins` : "N/A";
    recipePrepTime.textContent = recipe.prep_time ? `${recipe.prep_time} mins` : "N/A";
    recipeCookTime.textContent = recipe.cook_time ? `${recipe.cook_time} mins` : "N/A";
    recipeServes.textContent = recipe.serves || "N/A";

    // Render Nutrition Information
    nutritionTableBody.innerHTML = "";
    const nutrients = recipe.nutrients || {};
    for (const [key, value] of Object.entries(nutrients)) {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${key}</td><td>${value}</td>`;
        nutritionTableBody.appendChild(row);
    }

    drawer.classList.add("open");
    overlay.style.display = "block";
}

// Close Drawer
function closeDrawer() {
    drawer.classList.remove("open");
    overlay.style.display = "none";
}

// Utility Functions
function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}

function renderStars(rating) {
    const fullStars = Math.floor(rating || 0);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;

    return (
        "★".repeat(fullStars) +
        (halfStar ? "½" : "") +
        "☆".repeat(emptyStars)
    );
}

function showNoResultsMessage() {
    noResultsMessage.style.display = "block";
    recipeTableBody.innerHTML = "";
}

function showNoDataMessage() {
    noDataMessage.style.display = "block";
    recipeTableBody.innerHTML = "";
}

function hideMessages() {
    noResultsMessage.style.display = "none";
    noDataMessage.style.display = "none";
}

// Event Listeners
prevPageButton.addEventListener("click", () => {
    currentPage--;
    fetchRecipes();
});

nextPageButton.addEventListener("click", () => {
    currentPage++;
    fetchRecipes();
});

perPageSelect.addEventListener("change", (e) => {
    resultsPerPage = parseInt(e.target.value, 10);
    currentPage = 1;
    fetchRecipes();
});

filterTitle.addEventListener("input", (e) => {
    filters.title = e.target.value;
    currentPage = 1;
    fetchRecipes();
});

filterCuisine.addEventListener("input", (e) => {
    filters.cuisine = e.target.value;
    currentPage = 1;
    fetchRecipes();
});

filterRating.addEventListener("input", (e) => {
    filters.rating = e.target.value;
    currentPage = 1;
    fetchRecipes();
});

filterTime.addEventListener("input", (e) => {
    filters.total_time = e.target.value;
    currentPage = 1;
    fetchRecipes();
});

filterServes.addEventListener("input", (e) => {
    filters.serves = e.target.value;
    currentPage = 1;
    fetchRecipes();
});

drawerCloseButton.addEventListener("click", closeDrawer);
overlay.addEventListener("click", closeDrawer);

// Initial Fetch
fetchRecipes();