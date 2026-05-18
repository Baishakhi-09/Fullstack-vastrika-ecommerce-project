"use strict";

document.addEventListener("DOMContentLoaded", function () {
    initProfileDropdown();
    initAdminSearch();
    initProductSearchRedirect();
    initExportDropdown();
    initFilterToggle();
    initDeleteModal();
    initSidebarToggle();
    initAdminLogin();
    initPasswordToggle();
    initPasswordHelp();
    initNotifications();
    initSidebarSections();
    initSettingsSearch();
    initDashboardCharts();
    initProductAutoSlug();
    initSeoCharacterCounters();
    initProductFormEnhancements();
});

/* =========================
   Profile Dropdown
========================= */
function initProfileDropdown() {
    const trigger = document.getElementById("profileTrigger");
    const menu = document.getElementById("profileMenu");
    const dropdown = document.getElementById("profileDropdown");

    if (!trigger || !menu || !dropdown) return;

    trigger.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdown.classList.toggle("is-open");
    });

    document.addEventListener("click", function (e) {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove("is-open");
        }
    });
}

/* =========================
   Admin Search Suggestions
========================= */
function initAdminSearch() {
    const adminSearch = document.getElementById("admin-search");
    const searchSuggestions =
        document.getElementById("searchSuggestions") ||
        document.getElementById("searchDropdown");

    if (!adminSearch || !searchSuggestions) return;

    adminSearch.addEventListener("focus", function () {
        searchSuggestions.classList.add("is-open");
    });

    adminSearch.addEventListener("input", function () {
        const query = adminSearch.value.toLowerCase().trim();
        const items = searchSuggestions.querySelectorAll(".search-item");

        let hasVisible = false;

        items.forEach(function (item) {
            const text = item.innerText.toLowerCase();
            const match = text.includes(query);

            item.style.display = match || query === "" ? "flex" : "none";

            if (match || query === "") {
                hasVisible = true;
            }
        });

        searchSuggestions.classList.toggle("open", hasVisible);
    });

    document.addEventListener("click", function (e) {
        if (!e.target.closest(".search-form")) {
            searchSuggestions.classList.remove("open");
        }
    });
}

/* =========================
   Product Search Redirect
========================= */
function initProductSearchRedirect() {
    const searchForm = document.querySelector(
        "#changelist-search form"
    );
    if (!searchForm) return;

    searchForm.setAttribute("method", "GET");

    searchForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const searchInput = searchForm.querySelector(
            'input[name="q"]'
        );

        if (!searchInput) return;
        const query = searchInput.value.trim();
        if (!query) return;
        window.location.href =
            `/dashboard/products/product/search/${encodeURIComponent(query)}/`;
    });
}

/* =========================
   Export Dropdown
========================= */
function initExportDropdown() {

    const dropdowns = document.querySelectorAll(
        ".export-dropdown"
    );

    if (!dropdowns.length) return;

    dropdowns.forEach(function (dropdown) {

        const button = dropdown.querySelector(
            ".export-toggle-btn"
        );

        if (!button) return;

        button.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            dropdown.classList.toggle("is-open");
        });
    });

    document.addEventListener("click", function () {
        dropdowns.forEach(function (dropdown) {
            dropdown.classList.remove("is-open");
        });
    });
}

/* =========================
   Filter Toggle
========================= */
function initFilterToggle() {

    const layout = document.querySelector(
        "#product-layout"
    );

    const toggleButton = document.querySelector(
        "#toggle-filters"
    );

    if (!layout || !toggleButton) return;

    toggleButton.addEventListener("click", function () {

        layout.classList.toggle(
            "filters-visible"
        );

        layout.classList.toggle(
            "filters-hidden"
        );
    });
}

/* =========================
   Sidebar Toggle
========================= */
function initSidebarToggle() {
    const menuToggle = document.getElementById("menuToggle");

    if (!menuToggle) return;

    menuToggle.addEventListener("click", function () {
        document.body.classList.toggle("sidebar-open");
    });
}

/* =========================
   Admin Login
========================= */
function initAdminLogin() {
    const usernameInput = document.getElementById("id_username");
    const passwordInput = document.getElementById("id_password");
    const toggleBtn = document.getElementById("passwordToggle");
    const toggleIcon = document.getElementById("passwordToggleIcon");
    const loginForm = document.getElementById("login-form");
    const submitBtn = document.getElementById("loginSubmitBtn");

    if (usernameInput) {
        usernameInput.setAttribute("placeholder", "Enter your username");
    }

    if (passwordInput) {
        passwordInput.setAttribute("placeholder", "Enter your password");
    }

    if (toggleBtn && passwordInput && toggleIcon) {
        toggleBtn.addEventListener("click", function (e) {
            e.preventDefault();

            const isHidden = passwordInput.type === "password";
            passwordInput.type = isHidden ? "text" : "password";
            toggleIcon.textContent = isHidden ? "visibility" : "visibility_off";
        });
    }

    if (loginForm && submitBtn) {
        loginForm.addEventListener("submit", function () {
            submitBtn.classList.add("is-loading");
        });
    }
}

/* =========================
   Password Show / Hide Toggle
========================= */
function initPasswordToggle() {
    const toggles = document.querySelectorAll(".toggle-password");

    if (!toggles.length) return;

    toggles.forEach(function (toggle) {
        toggle.addEventListener("click", function () {
            const wrapper = toggle.closest(".admin-password-wrapper");
            if (!wrapper) return;

            const input = wrapper.querySelector("input");
            if (!input) return;

            const isHidden = input.type === "password";

            input.type = isHidden ? "text" : "password";
            toggle.textContent = isHidden ? "visibility_off" : "visibility";
        });
    });
}

/* =========================
   Password Help Show / Hide
========================= */
function initPasswordHelp() {
    const passwordInput = document.querySelector('input[name="new_password1"]');
    const helpBox = document.querySelector(".admin-password-help");

    if (!passwordInput || !helpBox) return;

    helpBox.classList.remove("show");

    passwordInput.addEventListener("focus", function () {
        if (passwordInput.value.trim().length === 0) {
            helpBox.classList.add("show");
        }
    });

    passwordInput.addEventListener("input", function () {
        if (passwordInput.value.trim().length > 0) {
            helpBox.classList.remove("show");
        } else {
            helpBox.classList.add("show");
        }
    });

    passwordInput.addEventListener("blur", function () {
        helpBox.classList.remove("show");
    });
}

/* =========================
   Dynamic Admin Notifications
========================= */
function initNotifications() {
    const notificationDropdown = document.getElementById("notificationDropdown");
    const notificationTrigger = document.getElementById("notificationTrigger");
    const notificationBadge = document.getElementById("notificationBadge");
    const notificationList = document.getElementById("notificationList");
    const markAllBtn = document.getElementById("markAllNotifications");

    if (!notificationBadge || !notificationList) return;

    let previousNotificationCount = 0;

    const NOTIFICATION_API = {
        LIST: "/api/products/admin-notifications/",
        MARK_ALL: "/api/products/admin-notifications/mark-all-read/",
    };

    async function loadNotifications() {
        try {
            const response = await fetch(NOTIFICATION_API.LIST, {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                console.error("Notification API error:", response.status);
                return;
            }

            const data = await response.json();
            const count = Number(data.count || data.unread_count || 0);

            playNotificationSound(count, previousNotificationCount);
            previousNotificationCount = count;

            updateNotificationBadge(notificationBadge, count);
            renderNotifications(notificationList, data.notifications || []);
        } catch (error) {
            console.error("Notification load error:", error);
        }
    }

    if (markAllBtn) {
        markAllBtn.addEventListener("click", async function () {
            await fetch("/api/products/admin-notifications/mark-all-read/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                credentials: "same-origin",
            });

            loadNotifications();
        });
    }

    notificationList.addEventListener("click", async function (e) {
        const item = e.target.closest(".notification-item");
        if (!item) return;

        const id = item.dataset.id;
        if (!id) return;

        await fetch(`/api/products/admin-notifications/mark-read/${id}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            credentials: "same-origin",
        });
    });

    loadNotifications();

    if (notificationDropdown) {
        setInterval(loadNotifications, 15000);
    }
}

/* =========================
   Notification Helpers
========================= */
function updateNotificationBadge(badge, count) {
    badge.textContent = count;
    badge.style.display = count > 0 ? "flex" : "none";
}

function renderNotifications(list, notifications) {
    if (!notifications.length) {
        list.innerHTML = `<div class="notification-empty">No new notifications</div>`;
        return;
    }

    list.innerHTML = notifications
        .map(function (item) {
            return `
                <a href="${escapeHtml(item.url || "#")}" class="notification-item unread" data-id="${item.id}">
                    <span class="material-icons">${notificationIcon(item.type)}</span>
                    <div>
                        <strong>${escapeHtml(item.title)}</strong>
                        <p>${escapeHtml(item.message)}</p>
                        <small>${escapeHtml(item.created_at)}</small>
                    </div>
                </a>
            `;
        })
        .join("");
}

function playNotificationSound(currentCount, previousCount) {
    if (currentCount <= previousCount || previousCount === 0) return;

    const sound = document.getElementById("notificationSound");

    if (!sound) return;

    sound.currentTime = 0;
    sound.play().catch(function () {});
}

function notificationIcon(type) {
    const icons = {
        order: "shopping_cart",
        product: "inventory_2",
        customer: "person_add",
        stock: "warning",
        system: "settings",
    };

    return icons[type] || "notifications";
}

/* =========================
   Utility Helpers
========================= */
function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return null;
}

function escapeHtml(value) {
    if (value === null || value === undefined) return "";

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

/* =========================
   Sidebar Collapsible Sections
========================= */
function initSidebarSections() {
    const groups = document.querySelectorAll(".sidebar-group");

    if (!groups.length) return;

    groups.forEach(function (group) {
        const btn = group.querySelector(".sidebar-section-toggle");

        if (!btn) return;

        // Toggle open/close
        btn.addEventListener("click", function () {
            groups.forEach(function (g) {
                if (g !== group) {
                    g.classList.remove("is-open");
                }
            });

            group.classList.toggle("is-open");
        });

        // Auto open active section
        if (group.querySelector(".sidebar-link.active")) {
            group.classList.add("is-open");
        }
    });
}

/* =========================
   Settings Search
========================= */
function initSettingsSearch() {
    const searchInput = document.getElementById("settingsSearch");
    const rows = document.querySelectorAll(".settings-row");
    const empty = document.getElementById("settingsEmpty");

    if (!searchInput || !rows.length) return;

    searchInput.addEventListener("input", function () {
        const keyword = this.value.toLowerCase().trim();
        let visibleCount = 0;

        rows.forEach(function (row) {
            const text = (row.dataset.search || "").toLowerCase();

            if (text.includes(keyword)) {
                row.style.display = "grid";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        if (empty) {
            empty.style.display = visibleCount === 0 ? "block" : "none";
        }
    });
}

/* =========================
   Dashboard Charts
========================= */
function initDashboardCharts() {
    if (typeof Chart === "undefined") return;

    function readJsonScript(id, fallback = []) {
        const element = document.getElementById(id);

        if (!element) {
            return fallback;
        }

        try {
            return JSON.parse(element.textContent);
        } catch (error) {
            console.error(`Invalid JSON for ${id}`, error);
            return fallback;
        }
    }

    const salesLabels = readJsonScript("sales-labels-data");
    const salesData = readJsonScript("sales-values-data");

    const categoryLabels = readJsonScript("category-labels-data");
    const categoryData = readJsonScript("category-values-data");

    const activityLabels = readJsonScript("activity-labels-data");
    const activityData = readJsonScript("activity-values-data");

    const salesCanvas = document.getElementById("salesChart");
    const categoryCanvas = document.getElementById("categoryChart");

    const activityCanvas = document.getElementById("activityChart");

    // SALES CHART
    if (salesCanvas) {
        new Chart(salesCanvas, {
            type: "line",
            data: {
                labels: salesLabels,
                datasets: [
                    {
                        label: "Orders",
                        data: salesData,
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    // CATEGORY CHART
    if (categoryCanvas) {
        new Chart(categoryCanvas, {
            type: "doughnut",
            data: {
                labels: categoryLabels,
                datasets: [
                    {
                        data: categoryData,
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    /* =========================================
        PREMIUM SALES CATEGORY CHART
    ========================================= */

    if (
        activityCanvas &&
        activityData.length &&
        typeof ApexCharts !== "undefined"
    ) {

        const options = {
            series: activityData,
            chart: {
                type: "donut",
                height: 340,
                toolbar: {
                    show: false,
                },
            },

            labels: activityLabels,
            colors: [
                "#0f4c81",
                "#2563eb",
                "#38bdf8",
                "#7dd3fc",
            ],

            stroke: {
                width: 0,
            },

            dataLabels: {
                enabled: false,
            },

            legend: {
                position: "right",
                fontSize: "14px",
                fontWeight: 600,
                fontFamily: "'Amaranth', sans-serif",
                labels: {
                    colors: "#000",
                },

                itemMargin: {
                    vertical: 14,
                },
            },

            plotOptions: {
                pie: {
                    donut: {
                        size: "68%",
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                label: "Sales",
                                color: "#ffffff",
                                formatter: function () {
                                    return "100%";
                                },
                            },
                        },
                    },
                },
            },

            responsive: [
                {
                    breakpoint: 768,
                    options: {
                        legend: {
                            position: "bottom",
                        },
                    },
                },
            ],
        };

        const chart = new ApexCharts(
            activityCanvas,
            options
        );
        chart.render();
    }
}

/* =========================================
   DELETE CONFIRM MODAL
========================================= */

function initDeleteModal() {

    const form = document.querySelector(
        "#changelist-form"
    );

    const actionSelect = document.querySelector(
        "select[name='action']"
    );

    const submitButton = document.querySelector(
        ".actions button"
    );

    const modal = document.querySelector(
        "#delete-modal"
    );

    const cancelButton = document.querySelector(
        "#modal-cancel-btn"
    );

    const confirmButton = document.querySelector(
        "#modal-delete-btn"
    );

    if (
        !form ||
        !actionSelect ||
        !submitButton ||
        !modal
    ) {
        return;
    }

    submitButton.addEventListener(
        "click",
        function (e) {

            const selectedAction =
                actionSelect.value;

            if (
                selectedAction === "delete_selected"
            ) {

                e.preventDefault();

                modal.classList.add(
                    "is-open"
                );
            }
        }
    );

    cancelButton.addEventListener(
        "click",
        function () {

            modal.classList.remove(
                "is-open"
            );
        }
    );

    modal.addEventListener(
        "click",
        function (e) {

            if (
                e.target.classList.contains(
                    "delete-modal-backdrop"
                )
            ) {

                modal.classList.remove(
                    "is-open"
                );
            }
        }
    );

    confirmButton.addEventListener(
        "click",
        function () {

            form.submit();
        }
    );
}

/* =========================================
   PRODUCT AUTO SLUG
========================================= */

function initProductAutoSlug() {

    const nameField = document.getElementById(
        "id_name"
    );

    const slugField = document.getElementById(
        "id_slug"
    );

    if (!nameField || !slugField) {
        return;
    }

    nameField.addEventListener(
        "input",
        function () {

            const slug = nameField.value
                .toLowerCase()
                .trim()
                .replace(/[^a-z0-9]+/g, "-")
                .replace(/^-+|-+$/g, "");

            slugField.value = slug;
        }
    );
}


/* =========================================
   SEO CHARACTER COUNTERS
========================================= */

function initSeoCharacterCounters() {

    setupSeoCounter(
        "id_meta_title",
        "meta-title-counter"
    );

    setupSeoCounter(
        "id_meta_description",
        "meta-description-counter"
    );
}


function setupSeoCounter(
    fieldId,
    counterId
) {

    const field = document.getElementById(
        fieldId
    );

    const counter = document.getElementById(
        counterId
    );

    if (!field || !counter) {
        return;
    }

    updateCounter();

    field.addEventListener(
        "input",
        updateCounter
    );

    function updateCounter() {

        counter.textContent =
            field.value.length;
    }
}


/* =========================================
   PRODUCT FORM UX
========================================= */

function initProductFormEnhancements() {

    const fields = document.querySelectorAll(
        ".admin-card input, .admin-card textarea, .admin-card select"
    );

    if (!fields.length) {
        return;
    }

    fields.forEach(function (field) {

        field.addEventListener(
            "focus",
            function () {

                const formGroup =
                    field.closest(".form-group");

                if (formGroup) {
                    formGroup.classList.add(
                        "is-focused"
                    );
                }
            }
        );

        field.addEventListener(
            "blur",
            function () {

                const formGroup =
                    field.closest(".form-group");

                if (formGroup) {
                    formGroup.classList.remove(
                        "is-focused"
                    );
                }
            }
        );
    });
}