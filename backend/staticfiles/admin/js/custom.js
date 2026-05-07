document.addEventListener("DOMContentLoaded", function () {
    const trigger = document.getElementById("profileTrigger");
    const menu = document.getElementById("profileMenu");
    const dropdown = document.getElementById("profileDropdown");

    const adminSearch = document.getElementById("admin-search");
    const searchSuggestions = document.getElementById("searchSuggestions");

    const menuToggle = document.getElementById("menuToggle");

    if (trigger && menu && dropdown) {
        trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            menu.classList.toggle("show");
        });

        document.addEventListener("click", function (e) {
            if (!dropdown.contains(e.target)) {
                menu.classList.remove("show");
            }
        });
    }

    if (adminSearch && searchSuggestions) {
        adminSearch.addEventListener("focus", function () {
            searchSuggestions.classList.add("open");
        });

        adminSearch.addEventListener("input", function () {
            const query = adminSearch.value.toLowerCase().trim();
            const items = searchSuggestions.querySelectorAll(".search-item");

            let hasVisible = false;

            items.forEach(function (item) {
                const text = item.innerText.toLowerCase();
                const match = text.includes(query);
                item.style.display = match || query === "" ? "flex" : "none";
                if (match || query === "") hasVisible = true;
            });

            searchSuggestions.classList.toggle("open", hasVisible);
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest(".search-form")) {
                searchSuggestions.classList.remove("open");
            }
        });
    }

    if (menuToggle) {
        menuToggle.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-open");
        });
    }
});


// Admin Login
document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("id_password");
    const toggleBtn = document.getElementById("passwordToggle");
    const toggleIcon = document.getElementById("passwordToggleIcon");
    const loginForm = document.getElementById("login-form");
    const submitBtn = document.getElementById("loginSubmitBtn");

    if (passwordInput) {
        passwordInput.setAttribute("placeholder", "Enter your password");
    }

    const usernameInput = document.getElementById("id_username");
    if (usernameInput) {
        usernameInput.setAttribute("placeholder", "Enter your username");
        usernameInput.focus();
    }

    if (toggleBtn && passwordInput && toggleIcon) {
        toggleBtn.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            toggleIcon.textContent = isPassword ? "visibility" : "visibility_off";
        });
    }

    if (loginForm && submitBtn) {
        loginForm.addEventListener("submit", function () {
            submitBtn.classList.add("is-loading");
        });
    }
});