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

        if (!hasResults) {
            notFound.style.display = "block";
        } else {
            notFound.style.display = "none";
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
            let formActionUrl;

            if (itemType === 'recipe') {
                formActionUrl = `/delete_recipe/${itemId}`;
            } else if (itemType === 'account') {
                formActionUrl = `/delete_account/${itemId}`;
            }

            // Create a form dynamically to submit as POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = formActionUrl;

            // CSRF token field if needed
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);

            // Append the form to the body and submit
            document.body.appendChild(form);
            form.submit();
        });
    }

    // Share buttons functionality 
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(button => {
        button.addEventListener('click', function () {
            const shareUrl = this.getAttribute('data-url');
            const shareText = this.getAttribute('data-text');
            const platform = this.getAttribute('data-platform');
            let url = '';

            if (platform === 'facebook') {
                url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
            } else if (platform === 'twitter') {
                url = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
            } else if (platform === 'whatsapp') {
                url = `https://wa.me/?text=${encodeURIComponent(shareText)}%20${encodeURIComponent(shareUrl)}`;
            }

            window.open(url, '_blank');
        });
    });

    // Function to update the user's points in real-time
    function updatePoints() {
        const protocol = window.location.protocol;  // Ensure HTTPS is used if the page is served over HTTPS
        const host = window.location.host;  // Get the correct host
        const apiUrl = `${protocol}//${host}/api/get_user_points`;  // Construct the API URL

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const pointsElement = document.getElementById("points-balance");
                if (pointsElement) {
                    pointsElement.textContent = `${data.points} Points`;
                }
            })
            .catch(error => {
                console.error("Error fetching user points:", error);
                // Display an error message to the user
                const pointsElement = document.getElementById("points-balance");
                if (pointsElement) {
                    pointsElement.textContent = "Error loading points";
                }
            });
    }

    // Check if user is authenticated before updating points
    const isAuthenticated = document.body.getAttribute('data-authenticated') === 'True';

    if (isAuthenticated) {
        // Call updatePoints when the page loads
        updatePoints();
    }
});
