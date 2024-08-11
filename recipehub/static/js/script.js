// Ensure the DOM is fully loaded before executing scripts
document.addEventListener("DOMContentLoaded", function () {
    // Function to filter recipes based on search input and category selection
    function filterRecipes() {
        const searchInput = document.getElementById("search");
        const categoryFilter = document.getElementById("categoryFilter");
        const recipes = document.querySelectorAll(".recipe-item");
        const notFound = document.getElementById("not-found");

        const searchValue = searchInput ? searchInput.value.trim().toLowerCase() : "";
        const selectedCategory = categoryFilter ? categoryFilter.value.toLowerCase() : "";
        let hasResults = false;

        recipes.forEach(function (card) {
            const recipeTitle = card.querySelector(".recipe-name").textContent.trim().toLowerCase();
            const recipeCategory = card.getAttribute("data-category").toLowerCase();

            const matchesSearch = recipeTitle.includes(searchValue);
            const matchesCategory = selectedCategory === "" || recipeCategory === selectedCategory;

            if (matchesSearch && matchesCategory) {
                card.style.display = "block";
                hasResults = true;
            } else {
                card.style.display = "none";
            }
        });

        if (notFound) {
            notFound.style.display = hasResults ? "none" : "block";
        }
    }

    // Event listeners for search and filter functionality
    const searchInput = document.getElementById("search");
    const filterForm = document.getElementById("filterForm");

    if (searchInput) {
        searchInput.addEventListener("input", filterRecipes);
    }

    if (filterForm) {
        filterForm.addEventListener("submit", function (e) {
            e.preventDefault();
            filterRecipes();
        });
    }

    // Delete confirmation modal functionality
    const deleteModal = document.getElementById('delete-modal');
    if (deleteModal) {
        $('#delete-modal').on('show.bs.modal', function (event) {
            const button = $(event.relatedTarget);
            const itemId = button.data('item-id');
            const itemType = button.data('item-type');
            const modal = $(this);

            modal.find('#item-type').text(itemType);
            $('#confirm-delete-btn').data('item-id', itemId);
            $('#confirm-delete-btn').data('item-type', itemType);
        });

        $('#confirm-delete-btn').click(function () {
            const itemId = $(this).data('item-id');
            const itemType = $(this).data('item-type');
            let deleteUrl;

            if (itemType === 'recipe') {
                deleteUrl = '/delete_recipe/' + itemId;
            } else if (itemType === 'account') {
                deleteUrl = '/delete_account/' + itemId;
            }

            window.location.href = deleteUrl;
        });
    }
});
