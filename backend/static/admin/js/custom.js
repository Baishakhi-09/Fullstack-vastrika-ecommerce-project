"use strict";

/* =========================================================
   GLOBAL APP INITIALIZER
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    initializeAdminApp();
});

function initializeAdminApp() {
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
    initProductSaveButtons();
    initSelect2Fixes();
    initBasicInformationUI();
    initMediaGallery();

    initSelect2AccessibilityFix();
    initPricingCalculator();
    initInventorySystem();
    initShippingSystem();

    // initVariantSystem();
    initSeoSystem();
    initProductSidebar();

    /* BRAND */
    initBrandAutoSlug();
    initBrandFilePreview();
    initBrandLogoUpload();
    initBrandSidebarActions();
}

/* =========================================================
   SHARED HELPERS
========================================================= */

function qs(selector, scope = document) {
    return scope.querySelector(selector);
}

function qsa(selector, scope = document) {
    return [...scope.querySelectorAll(selector)];
}

function on(element, event, handler, options = false) {
    if (!element) return;
    element.addEventListener(event, handler, options);
}

function toggleClass(element, className) {
    if (!element) return;
    element.classList.toggle(className);
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getCookie(name) {
    const cookies = document.cookie
        ? document.cookie.split(";")
        : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(`${name}=`)) {
            return decodeURIComponent(
                cookie.substring(name.length + 1)
            );
        }
    }

    return null;
}

function debounce(callback, delay = 300) {
    let timeout;

    return function (...args) {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            callback.apply(this, args);
        }, delay);
    };
}

/* =========================================================
   API CLIENT
========================================================= */

window.apiClient = window.apiClient || {
    async get(url) {
        const response = await fetch(url, {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        if (!response.ok) {
            throw new Error(
                `GET ${url} failed (${response.status})`
            );
        }

        return response.json();
    },

    async post(url, data = {}) {
        const response = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(
                `POST ${url} failed (${response.status})`
            );
        }

        return response.json();
    },
};

/* =========================================================
   PROFILE DROPDOWN
========================================================= */

function initProfileDropdown() {
    const trigger = qs("#profileTrigger");
    const menu = qs("#profileMenu");
    const dropdown = qs("#profileDropdown");

    if (!trigger || !menu || !dropdown) {
        return;
    }

    on(trigger, "click", (event) => {
        event.stopPropagation();
        dropdown.classList.toggle("is-open");
        trigger.setAttribute(
            "aria-expanded",
            dropdown.classList.contains("is-open")
        );
    });

    on(document, "click", (event) => {
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove("is-open");
            trigger.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    });
}

/* =========================================================
   ADMIN SEARCH
========================================================= */

function initAdminSearch() {
    const input = qs("#admin-search");
    const suggestions =
        qs("#searchSuggestions") ||
        qs("#searchDropdown");

    if (!input || !suggestions) {
        return;
    }

    on(input, "focus", () => {
        suggestions.classList.add("is-open");
    });

    on(
        input,
        "input",
        debounce(function () {
            const keyword =
                input.value.toLowerCase().trim();
            const items = qsa(
                ".search-item",
                suggestions
            );

            let visible = 0;
            items.forEach((item) => {
                const text =
                    item.textContent.toLowerCase();

                const matched =
                    text.includes(keyword);

                item.style.display =
                    matched || keyword === ""
                        ? "flex"
                        : "none";

                if (matched || keyword === "") {
                    visible += 1;
                }
            });

            suggestions.classList.toggle(
                "is-open",
                visible > 0
            );
        }, 250)
    );

    on(document, "click", (event) => {
        if (!event.target.closest(".search-form")) {
            suggestions.classList.remove(
                "is-open"
            );
        }
    });
}

/* =========================================================
   PRODUCT SEARCH REDIRECT
========================================================= */

function initProductSearchRedirect() {
    const form = qs("#changelist-search form");
    if (!form) {
        return;
    }

    form.setAttribute("method", "GET");
    on(form, "submit", (event) => {
        event.preventDefault();
        const input = qs(
            'input[name="q"]',
            form
        );

        if (!input) {
            return;
        }

        const query = input.value.trim();

        if (!query) {
            return;
        }

        window.location.href =
            `/dashboard/products/product/search/${encodeURIComponent(query)}/`;
    });
}

/* =========================================================
   EXPORT DROPDOWN
========================================================= */

function initExportDropdown() {
    const dropdowns = qsa(".export-dropdown");
    if (!dropdowns.length) {
        return;
    }

    dropdowns.forEach((dropdown) => {
        const button = qs(
            ".export-toggle-btn",
            dropdown
        );

        if (!button) {
            return;
        }

        on(button, "click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropdown.classList.toggle("is-open");
        });
    });

    on(document, "click", () => {
        dropdowns.forEach((dropdown) => {
            dropdown.classList.remove("is-open");
        });
    });
}

/* =========================================================
   FILTER TOGGLE
========================================================= */

function initFilterToggle() {
    const layout = qs("#product-layout");
    const button = qs("#toggle-filters");

    if (!layout || !button) {
        return;
    }

    on(button, "click", () => {
        layout.classList.toggle(
            "filters-visible"
        );

        layout.classList.toggle(
            "filters-hidden"
        );
    });
}

/* =========================================================
   SIDEBAR TOGGLE
========================================================= */

function initSidebarToggle() {
    const menuToggle = qs("#menuToggle");

    if (!menuToggle) {
        return;
    }

    on(menuToggle, "click", () => {
        document.body.classList.toggle(
            "sidebar-open"
        );
    });
}

/* =========================================================
   ADMIN LOGIN
========================================================= */

function initAdminLogin() {
    const usernameInput = qs("#id_username");
    const passwordInput = qs("#id_password");
    const toggleButton = qs("#passwordToggle");

    const toggleIcon = qs(
        "#passwordToggleIcon"
    );

    const loginForm = qs("#login-form");
    const submitButton = qs(
        "#loginSubmitBtn"
    );

    if (usernameInput) {
        usernameInput.setAttribute(
            "placeholder",
            "Enter your username"
        );
    }

    if (passwordInput) {
        passwordInput.setAttribute(
            "placeholder",
            "Enter your password"
        );
    }

    if (
        toggleButton &&
        passwordInput &&
        toggleIcon
    ) {

        on(toggleButton, "click", (event) => {
            event.preventDefault();
            const hidden =
                passwordInput.type === "password";

            passwordInput.type =
                hidden ? "text" : "password";

            toggleIcon.textContent =
                hidden
                    ? "visibility"
                    : "visibility_off";
        });
    }

    if (loginForm && submitButton) {
        on(loginForm, "submit", () => {
            submitButton.classList.add(
                "is-loading"
            );

            submitButton.disabled = true;
        });
    }
}

/* =========================================================
   PASSWORD TOGGLE
========================================================= */

function initPasswordToggle() {
    const toggles = qsa(".toggle-password");
    if (!toggles.length) {
        return;
    }

    toggles.forEach((toggle) => {
        on(toggle, "click", () => {
            const wrapper =
                toggle.closest(
                    ".admin-password-wrapper"
                );

            if (!wrapper) {
                return;
            }

            const input =
                qs("input", wrapper);

            if (!input) {
                return;
            }

            const hidden =
                input.type === "password";

            input.type =
                hidden ? "text" : "password";

            toggle.textContent =
                hidden
                    ? "visibility_off"
                    : "visibility";
        });
    });
}

/* =========================================================
   PASSWORD HELP
========================================================= */

function initPasswordHelp() {
    const input = qs(
        'input[name="new_password1"]'
    );

    const helpBox = qs(
        ".admin-password-help"
    );

    if (!input || !helpBox) {
        return;
    }

    helpBox.classList.remove("show");
    on(input, "focus", () => {
        if (!input.value.trim()) {
            helpBox.classList.add("show");
        }
    });

    on(input, "input", () => {
        helpBox.classList.toggle(
            "show",
            !input.value.trim()
        );
    });

    on(input, "blur", () => {
        helpBox.classList.remove("show");
    });
}

/* =========================================================
   NOTIFICATIONS
========================================================= */

function initNotifications() {
    const badge = qs("#notificationBadge");
    const list = qs("#notificationList");
    const markAllButton = qs(
        "#markAllNotifications"
    );

    const dropdown = qs(
        "#notificationDropdown"
    );

    const trigger = qs(
        "#notificationTrigger"
    );

    const panel = qs(
        "#notificationPanel"
    );

    if (!badge || !list || !trigger || !panel) {
        return;
    }

    let previousCount = 0;

    const API = {
        LIST:
            "/api/products/admin-notifications/",

        MARK_ALL:
            "/api/products/admin-notifications/mark-all-read/",
    };

    on(trigger, "click", (event) => {
        event.stopPropagation();

        dropdown.classList.toggle(
            "is-open"
        );
    });

    on(document, "click", () => {
        dropdown.classList.remove(
            "is-open"
        );
    });

    on(panel, "click", (event) => {
        event.stopPropagation();
    });


    async function loadNotifications() {
        try {
            const data =
                await apiClient.get(API.LIST);

            const count = Number(
                data.count ??
                data.unread_count ??
                0
            );

            playNotificationSound(
                count,
                previousCount
            );

            previousCount = count;

            updateNotificationBadge(
                badge,
                count
            );

            renderNotifications(
                list,
                data.notifications || []
            );

        } catch (error) {
            console.error(
                "Notification error:",
                error
            );

            list.innerHTML = `
                <div class="notification-empty">
                    Failed to load notifications
                </div>`;
        }
    }

    if (markAllButton) {
        on(markAllButton, "click", async (event) => {
            event.stopPropagation();

            try {
                await apiClient.post(
                    API.MARK_ALL
                );

                loadNotifications();
            } catch (error) {
                console.error(
                    "Mark all read error:",
                    error
                );
            }
        });
    }

    loadNotifications();

    if (dropdown) {
        setInterval(
            loadNotifications,
            15000
        );
    }
}

/* =========================================================
   NOTIFICATION HELPERS
========================================================= */

function updateNotificationBadge(
    badge,
    count
) {
    badge.textContent = count;
    badge.hidden = count <= 0;
}

function renderNotifications(
    list,
    notifications
) {

    if (!notifications.length) {
        list.innerHTML = `
            <div class="notification-empty">
                No new notifications
            </div>
        `;
        return;
    }

    list.innerHTML = notifications
        .map((item) => {
            return `
                <a
                    href="${escapeHtml(item.url || "#")}"
                    class="notification-item unread"
                    data-id="${item.id}">

                    <span class="material-icons notification-icon">
                        ${notificationIcon(item.type)}
                    </span>

                    <div class="notification-content">
                        <strong>
                            ${escapeHtml(item.title)}
                        </strong>

                        <p>
                            ${escapeHtml(item.message)}
                        </p>

                        <small>
                            ${escapeHtml(item.created_at)}
                        </small>
                    </div>
                </a>
            `;
        })
        .join("");
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

function playNotificationSound(
    current,
    previous
) {

    if (
        current <= previous ||
        previous === 0
    ) {
        return;
    }

    const sound = qs(
        "#notificationSound"
    );

    if (!sound) {
        return;
    }

    sound.currentTime = 0;
    sound.play().catch(() => {});
}

/* =========================================================
   SIDEBAR COLLAPSIBLE SECTIONS
========================================================= */

function initSidebarSections() {
    const groups = qsa(".sidebar-group");
    if (!groups.length) {
        return;
    }
    groups.forEach((group) => {
        const button = qs(
            ".sidebar-section-toggle",
            group
        );

        if (!button) {
            return;
        }

        on(button, "click", () => {
            groups.forEach((item) => {
                if (item !== group) {
                    item.classList.remove(
                        "is-open"
                    );
                }
            });

            group.classList.toggle(
                "is-open"
            );
        });

        if (
            qs(".sidebar-link.active", group)
        ) {

            group.classList.add("is-open");
        }
    });
}

/* =========================================================
   SETTINGS SEARCH
========================================================= */

function initSettingsSearch() {
    const input = qs("#settingsSearch");
    const rows = qsa(".settings-row");
    const empty = qs("#settingsEmpty");
    if (!input || !rows.length) {
        return;
    }

    on(
        input,
        "input",
        debounce(function () {
            const keyword =
                input.value.toLowerCase().trim();

            let visible = 0;

            rows.forEach((row) => {
                const text =
                    (
                        row.dataset.search || ""
                    ).toLowerCase();

                const matched =
                    text.includes(keyword);

                row.style.display =
                    matched ? "grid" : "none";

                if (matched) {
                    visible += 1;
                }
            });

            if (empty) {
                empty.style.display =
                    visible === 0
                        ? "block"
                        : "none";
            }
        }, 200)
    );
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

    // PREMIUM SALES CATEGORY CHART
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

/* =========================================================
   DELETE MODAL
========================================================= */

function initDeleteModal() {
    const form = 
        qs("#changelist-form");

    const actionSelect = 
        qs("select[name='action']");

    const modal = qs("#delete-modal");

    const cancelButton = 
        qs("#modal-cancel-btn");

    const confirmButton = qs(
        "#modal-delete-btn"
    );

    if (
        !form ||
        !actionSelect ||
        !modal
    ) {
        return;
    }

    let confirmed = false;

    form.addEventListener(
        "submit",
        function (event) {
            if (confirmed) {
                return;
            }

            const deleteActions = [
                "delete_selected_brands",

                "delete_selected_product_tags",

                "delete_selected_parentcategories",

                "delete_selected_subcategories",

                "delete_selected_childcategories",

                "delete_selected_productvariant",

                "delete_selected_warehouse",

                "delete_selected"
            ];

            if (
                deleteActions.includes(
                    actionSelect.value
                )
            ) {
                event.preventDefault();

                modal.classList.add(
                    "is-open"
                );
            }
        }
    );

    on(cancelButton, "click", () => {
        modal.classList.remove(
            "is-open"
        );
    });

    on(modal, "click", (event) => {
        if (
            event.target.classList.contains(
                "delete-modal-backdrop"
            )
        ) {
            modal.classList.remove(
                "is-open"
            );
        }
    });

    on(confirmButton, "click", () => {
        confirmed = true;

        modal.classList.remove(
            "is-open"
        );

        form.submit();
    });
}

/* =========================================================
   PRODUCT AUTO SLUG
========================================================= */

function initProductAutoSlug() {
    const nameField = qs("#id_name");
    const slugField = qs("#id_slug");
    if (!nameField || !slugField) {
        return;
    }

    on(nameField, "input", () => {
        slugField.value = nameField.value
            .toLowerCase()
            .trim()
            .replace(
                /[^a-z0-9]+/g,
                "-"
            )
            .replace(
                /^-+|-+$/g,
                ""
            );
    });
}

/* =========================================================
   SEO CHARACTER COUNTERS
========================================================= */

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

    const field = qs(`#${fieldId}`);
    const counter = qs(`#${counterId}`);
    if (!field || !counter) {
        return;
    }

    const update = () => {
        counter.textContent =
            field.value.length;
    };

    update();

    on(field, "input", update);
}

/* =========================================================
   PRODUCT FORM UX
========================================================= */

function initProductFormEnhancements() {
    const fields = qsa(
        ".admin-card input, .admin-card textarea, .admin-card select"
    );

    if (!fields.length) {
        return;
    }

    fields.forEach((field) => {
        on(field, "focus", () => {
            const group =
                field.closest(
                    ".form-group"
                );

            if (group) {
                group.classList.add(
                    "is-focused"
                );
            }
        });

        on(field, "blur", () => {
            const group =
                field.closest(
                    ".form-group"
                );

            if (group) {
                group.classList.remove(
                    "is-focused"
                );
            }
        });
    });
}

/* =========================================================
   SELECT2 HEIGHT FIX
========================================================= */

function initSelect2Fixes() {
    const select2Fields = document.querySelectorAll(
        ".select2-container"
    );

    if (!select2Fields.length) {
        return;
    }

    select2Fields.forEach((field) => {
        field.style.width = "100%";
    });
}

/* =========================================================
   SELECT2 ACCESSIBILITY FIX
========================================================= */

function initSelect2AccessibilityFix() {
    const observer = new MutationObserver(() => {
        document
            .querySelectorAll(
                ".select2-search__field"
            )
            .forEach((input, index) => {
                if (!input.id) {

                    input.id =
                        `select2-search-field-${
                            Date.now()
                        }-${Math.random()
                            .toString(36)
                            .slice(2, 8)}`;
                }

                if (!input.name) {

                    input.name =
                        `select2-search-field-${
                            Date.now()
                        }-${Math.random()
                            .toString(36)
                            .slice(2, 8)}`;
                }

                input.setAttribute(
                    "autocomplete",
                    "off"
                );

                input.setAttribute(
                    "aria-label",
                    "Search field"
                );
            });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

/* =========================================================
   BASIC INFORMATION UI FIX
========================================================= */

function initBasicInformationUI() {
    const select2Containers = document.querySelectorAll(
        ".select2-container"
    );

    if (!select2Containers.length) {
        return;
    }

    select2Containers.forEach((container) => {

        container.style.width = "100%";

        const selection = container.querySelector(
            ".select2-selection"
        );

        if (selection) {

            selection.style.width = "100%";

        }

    });

}

/* =========================================================
   PRODUCT FORM SAVE BUTTONS
========================================================= */

function initProductSaveButtons() {

    const form = document.getElementById(
        "product-admin-form"
    );

    if (!form) {
        return;
    }

    const saveButtons = form.querySelectorAll(
        ".primary-btn, .secondary-btn"
    );

    form.addEventListener(
        "submit",
        function () {

            const clickedButton =
                document.activeElement;

            saveButtons.forEach(
                function (button) {

                    if (button !== clickedButton) {
                        button.disabled = true;
                    }

                    button.classList.add(
                        "is-loading"
                    );

                    if (!button.dataset.originalText) {
                        button.dataset.originalText =
                            button.textContent.trim();
                    }

                }
            );

        },
        {
            once: true
        }
    );
}

/* =========================================================
   MEDIA GALLERY
========================================================= */

function initMediaGallery() {

    const manageImagesBtn = document.getElementById(
        "manage-product-images"
    );

    if (manageImagesBtn) {

        manageImagesBtn.addEventListener(
            "click",
            function () {

                const imageSection =
                    document.getElementById(
                        "product-images-section"
                    );

                if (imageSection) {

                    imageSection.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                    imageSection.classList.add(
                        "section-highlight"
                    );

                    setTimeout(() => {

                        imageSection.classList.remove(
                            "section-highlight"
                        );

                    }, 2000);
                }
            }
        );
    }
    
    const dropzone = document.getElementById(
        "mediaDropzone"
    );

    if (!dropzone) {
        return;
    }

    if (dropzone.dataset.initialized === "true") {
        return;
    }

    dropzone.dataset.initialized = "true";

    const input = document.getElementById(
        "id_images"
    );

    const previewGrid = document.getElementById(
        "mediaPreviewGrid"
    );

    const countBadge = document.querySelector(
        ".media-count-badge"
    );

    if (!input || !previewGrid || !countBadge) {
        return;
    }

    dropzone.addEventListener(
        "click",
        () => {
            input.click();
        }
    );

    [
        "dragenter",
        "dragover"
    ].forEach((eventName) => {

        dropzone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();
                event.stopPropagation();

                dropzone.classList.add(
                    "drag-active"
                );
            }
        );
    });

    [
        "dragleave",
        "drop"
    ].forEach((eventName) => {

        dropzone.addEventListener(
            eventName,
            (event) => {

                event.preventDefault();
                event.stopPropagation();

                dropzone.classList.remove(
                    "drag-active"
                );
            }
        );
    });

    dropzone.addEventListener(
        "drop",
        (event) => {
            const files = event.dataTransfer.files;
            
            if (!files || !files.length) {
                return;
            }

            renderMediaPreview(files);
        }
    );

    input.addEventListener(
        "change",
        (event) => {

            const files = event.target.files;

            if (!files || !files.length) {
                return;
            }

            renderMediaPreview(files);
        }
    );

    function renderMediaPreview(files) {
        previewGrid.innerHTML = "";

        const imageFiles = Array.from(files);

        countBadge.textContent =
            `${imageFiles.length} Images`;

        imageFiles.forEach((file) => {
            if (!file.type.startsWith("image/")) {
                return;
            }

            const reader = new FileReader();

            reader.onload = function (e) {
                const card = document.createElement(
                    "div"
                );

                card.className =
                    "media-preview-card";

                card.innerHTML = `
                    <img
                        src="${e.target.result}"
                        alt="${file.name}">
                `;

                previewGrid.appendChild(card);

            };

            reader.readAsDataURL(file);
        });
    }
}

/* =========================================================
   PRICING CALCULATOR
========================================================= */

function initPricingCalculator() {
    const sellingPriceInput = 
        document.getElementById("id_selling_price");

    const comparePriceInput = 
        document.getElementById("id_mrp");

    const costPriceInput = 
        document.getElementById("id_cost_price");

    const taxClassInput =
        document.getElementById("id_tax");

    const profitMarginValue = 
        document.getElementById("profitMarginValue");

    const profitValue =
        document.getElementById("profitValue");

    const discountValue = 
        document.getElementById("discountValue");

    const taxAmountValue =
        document.getElementById("taxAmountValue");
    
    const finalPriceValue =
        document.getElementById("finalPriceValue");

    if (
        !sellingPriceInput ||
        !comparePriceInput
    ) {
        return;
    }

    if (
        !profitMarginValue ||
        !profitValue ||
        !discountValue ||
        !taxAmountValue
    ) {
        return;
    }

    function updatePricingInsights() {
        const sellingPrice =
            parseFloat(
                sellingPriceInput.value
            ) || 0;

        const comparePrice =
            parseFloat(
                comparePriceInput.value
            ) || 0;

        const costPrice =
            parseFloat(
                costPriceInput?.value
            ) || 0;

        let estimatedProfit = 0;
        let profitMargin = 0;
        let discount = 0;
        let gstRate = 0;
        let taxAmount = 0;

        if (costPriceInput) {
            estimatedProfit =
                sellingPrice - costPrice;

            if (sellingPrice > 0) {
                profitMargin =
                    (
                        estimatedProfit /
                        sellingPrice
                    ) * 100;
            }
        }

        if (
            comparePrice > 0 &&
            sellingPrice > 0
        ) {
            discount =
                (
                    (
                        comparePrice -
                        sellingPrice
                    ) /
                    comparePrice
                ) * 100;
        }

        switch (taxClassInput?.value) {

            case "gst_5":
                gstRate = 5;
                break;

            case "gst_12":
                gstRate = 12;
                break;

            case "gst_18":
                gstRate = 18;
                break;

            case "gst_28":
                gstRate = 28;
                break;

                default:
                    gstRate = 0;
        }

        taxAmount =
            (sellingPrice * gstRate) / 100;

        const finalPrice =
            sellingPrice + taxAmount;

        if (finalPriceValue) {
            finalPriceValue.textContent =
                `₹${finalPrice.toFixed(2)}`;
        }

        profitMarginValue.textContent =
            `${profitMargin.toFixed(1)}%`;

        profitValue.textContent =
            `₹${estimatedProfit.toFixed(2)}`;

        discountValue.textContent =
            `${discount.toFixed(1)}%`;

        taxAmountValue.textContent =
            `₹${taxAmount.toFixed(2)}`;

        profitMarginValue.classList.remove(
            "profit-positive",
            "profit-warning",
            "profit-negative"
        );

        if (profitMargin >= 40) {
            profitMarginValue.classList.add(
                "profit-positive"
            );

        } else if (profitMargin >= 15) {
            profitMarginValue.classList.add(
                "profit-warning"
            );

        } else {
            profitMarginValue.classList.add(
                "profit-negative"
            );
        }
    }

    [
        sellingPriceInput,
        comparePriceInput,
        costPriceInput,
        taxClassInput
    ]
    .filter(Boolean)
    .forEach((input) => {
        input.addEventListener(
            "input",
            updatePricingInsights
        );

        input.addEventListener(
            "change",
            updatePricingInsights
        );
    });

    updatePricingInsights();
}

/* =========================================================
   INVENTORY SYSTEM
========================================================= */

function initInventorySystem() {
    const skuInput = document.getElementById(
        "id_sku"
    );

    const productNameInput = document.getElementById(
        "id_name"
    );

    const generateSkuBtn = document.getElementById(
        "generateSkuBtn"
    );

    const backorderInput = document.getElementById(
        "id_allow_backorders"
    );

    // const stockBadge = document.getElementById(
    //     "inventoryStatusBadge"
    // );
    
    const availableStockValue = document.getElementById(
        "availableStockValue"
    );

    const stockHealthValue = document.getElementById(
        "stockHealthValue"
    );

    // const thresholdInput = document.getElementById(
    //     "id_low_stock_threshold"
    // );

    const backorderValue = document.getElementById(
        "backorderValue"
    );

    if (
        generateSkuBtn &&
        skuInput &&
        productNameInput
    ) {
        generateSkuBtn.addEventListener(
            "click",
            () => {
                const name =
                    productNameInput.value
                        .trim()
                        .replace(/\s+/g, "-")
                        .toUpperCase()
                        .slice(0, 10);

                const random =
                    Math.floor(
                        1000 + Math.random() * 9000
                    );

                skuInput.value =
                    `${name}-${random}`;
            }
        );
    }

    function updateInventoryInsights() {
        // const threshold =
        //     parseInt(thresholdInput?.value) || 0;

        let stock = 0;

        if (
            availableStockValue &&
            availableStockValue.dataset.stock
        ) {
            stock =
                parseInt(
                    availableStockValue.dataset.stock
                ) || 0;
        }

        if (stockHealthValue) {
            stockHealthValue.classList.remove(
                "stock-healthy",
                "stock-warning",
                "stock-danger"
            );

            if (stock <= 0) {
                stockHealthValue.textContent =
                    "Out of Stock";

                stockHealthValue.classList.add(
                    "stock-danger"
                );

            } else if (stock <= 5) {
                stockHealthValue.textContent =
                    "Low Stock";

                stockHealthValue.classList.add(
                    "stock-warning"
                );

            } else {
                stockHealthValue.textContent =
                    "Healthy";

                stockHealthValue.classList.add(
                    "stock-healthy"
                );
            }
        }

        // if (stockBadge) {
        //     if (stock <= 0) {
        //         stockBadge.textContent =
        //             "Out of Stock";

        //         stockBadge.style.background =
        //             "#fee2e2";

        //         stockBadge.style.color =
        //             "#991b1b";

        //     } else if (stock <= threshold) {
        //         stockBadge.textContent =
        //             "Low Stock";

        //         stockBadge.style.background =
        //             "#fef3c7";

        //         stockBadge.style.color =
        //             "#92400e";

        //     } else {
        //         stockBadge.textContent =
        //             "In Stock";

        //         stockBadge.style.background =
        //             "#dcfce7";

        //         stockBadge.style.color =
        //             "#166534";
        //     }
        // }

        if (
            backorderInput &&
            backorderValue
        ) {
            backorderValue.innerHTML =
                backorderInput.checked
                    ? '<span class="badge-success">Enabled</span>'
                    : '<span class="badge-danger">Disabled</span>';
        }
    }

    [
        backorderInput
    ].forEach((input) => {
        if (!input) {
            return;
        }

        input.addEventListener(
            "input",
            updateInventoryInsights
        );

        input.addEventListener(
            "change",
            updateInventoryInsights
        );
    });

    updateInventoryInsights();
}

function initShippingSystem() {
    const lengthInput = document.getElementById(
        "id_length"
    );

    const widthInput = document.getElementById(
        "id_width"
    );

    const heightInput = document.getElementById(
        "id_height"
    );

    const weightInput = document.getElementById(
        "id_weight"
    );

    const freeShippingInput = document.getElementById(
        "id_free_shipping"
    );

    const packageSizeValue = document.getElementById(
        "packageSizeValue"
    );

    const shippingStatusValue = document.getElementById(
        "shippingStatusValue"
    );

    const deliveryTypeValue = document.getElementById(
        "deliveryTypeValue"
    );

    function updateShippingInsights() {
        const length =
            parseFloat(lengthInput?.value) || 0;

        const width =
            parseFloat(widthInput?.value) || 0;

        const height =
            parseFloat(heightInput?.value) || 0;

        const weight =
            parseFloat(weightInput?.value) || 0;

        const packageSize =
            length * width * height;

        if (packageSizeValue) {
            packageSizeValue.textContent =
                `${packageSize.toFixed(0)} cm³`;
        }

        if (shippingStatusValue) {
            if (weight >= 20) {
                shippingStatusValue.textContent =
                    "Heavy";

            } else if (weight >= 5) {
                shippingStatusValue.textContent =
                    "Medium";

            } else {
                shippingStatusValue.textContent =
                    "Standard";
            }
        }

        if (
            freeShippingInput &&
            deliveryTypeValue
        ) {
            deliveryTypeValue.textContent =
                freeShippingInput.checked
                    ? "Free"
                    : "Paid";
        }
    }

    [
        lengthInput,
        widthInput,
        heightInput,
        weightInput,
        freeShippingInput
    ].forEach((input) => {
        if (!input) {
            return;
        }

        input.addEventListener(
            "input",
            updateShippingInsights
        );

        input.addEventListener(
            "change",
            updateShippingInsights
        );
    });
}

/* =========================================================
   VARIANT SYSTEM
========================================================= */

// function initVariantSystem() {

//     const sizesInput = document.getElementById(
//         "variantSizes"
//     );

//     const colorsInput = document.getElementById(
//         "variantColors"
//     );

//     const generateBtn = document.getElementById(
//         "generateVariantsBtn"
//     );

//     const tableBody = document.getElementById(
//         "variantTableBody"
//     );

//     const totalVariantsValue = document.getElementById(
//         "totalVariantsValue"
//     );

//     const variantStockValue = document.getElementById(
//         "variantStockValue"
//     );

//     const variantStatusValue = document.getElementById(
//         "variantStatusValue"
//     );

//     if (
//         !sizesInput ||
//         !colorsInput ||
//         !generateBtn ||
//         !tableBody
//     ) {
//         return;
//     }

//     generateBtn.addEventListener(
//         "click",
//         () => {

//             const sizes =
//                 sizesInput.value
//                     .split(",")
//                     .map((item) => item.trim())
//                     .filter(Boolean);

//             const colors =
//                 colorsInput.value
//                     .split(",")
//                     .map((item) => item.trim())
//                     .filter(Boolean);

//             if (
//                 !sizes.length ||
//                 !colors.length
//             ) {

//                 alert(
//                     "Please enter at least one size and one color."
//                 );

//                 return;
//             }

//             tableBody.innerHTML = "";

//             let totalVariants = 0;
//             let totalStock = 0;

//             sizes.forEach((size) => {

//                 colors.forEach((color) => {

//                     totalVariants += 1;

//                     /* ---------------------------------
//                        DEMO STOCK
//                        Replace later with real stock
//                     --------------------------------- */

//                     const stock = 0;

//                     totalStock += stock;

//                     const sku =
//                         `${size}-${color}`
//                             .replace(/\s+/g, "-")
//                             .toUpperCase();

//                     const sellingPrice =
//                         document.getElementById(
//                             "id_selling_price"
//                         )?.value || "0";

//                     const row =
//                         document.createElement("tr");

//                     row.innerHTML = `
//                         <td>${sku}</td>

//                         <td>${size}</td>

//                         <td>${color}</td>

//                         <td>${stock}</td>

//                         <td>₹${sellingPrice}</td>

//                         <td>
//                             <span
//                                 class="variant-status-badge variant-status-active">

//                                 Active
//                             </span>
//                         </td>
//                     `;

//                     tableBody.appendChild(row);
//                 });
//             });

//             if (totalVariantsValue) {

//                 totalVariantsValue.textContent =
//                     totalVariants;
//             }

//             if (variantStockValue) {

//                 variantStockValue.textContent =
//                     totalStock;
//             }

//             if (variantStatusValue) {

//                 variantStatusValue.textContent =
//                     totalVariants > 0
//                         ? "Generated"
//                         : "Empty";
//             }

//             const availableStockValue =
//                 document.getElementById(
//                     "availableStockValue"
//                 );

//             const stockHealthValue =
//                 document.getElementById(
//                     "stockHealthValue"
//                 );

//             const stockBadge =
//                 document.getElementById(
//                     "inventoryStatusBadge"
//                 );

//             const thresholdInput =
//                 document.getElementById(
//                     "id_low_stock_threshold"
//                 );

//             if (availableStockValue) {

//                 availableStockValue.dataset.stock =
//                     totalStock;

//                 availableStockValue.textContent =
//                     `${totalStock} Units`;
//             }

//             const threshold =
//                 parseInt(
//                     thresholdInput?.value
//                 ) || 0;

//             if (stockHealthValue) {
//                 stockHealthValue.classList.remove(
//                     "stock-healthy",
//                     "stock-warning",
//                     "stock-danger"
//                 );

//                 if (totalStock <= 0) {

//                     stockHealthValue.textContent =
//                         "Out of Stock";

//                     stockHealthValue.classList.add(
//                         "stock-danger"
//                     );

//                 } else if (
//                     totalStock <= threshold
//                 ) {

//                     stockHealthValue.textContent =
//                         "Low Stock";

//                     stockHealthValue.classList.add(
//                         "stock-warning"
//                     );

//                 } else {

//                     stockHealthValue.textContent =
//                         "Healthy";

//                     stockHealthValue.classList.add(
//                         "stock-healthy"
//                     );
//                 }
//             }

//             if (stockBadge) {
//                 if (totalStock <= 0) {

//                     stockBadge.textContent =
//                         "Out of Stock";

//                     stockBadge.style.background =
//                         "#fee2e2";

//                     stockBadge.style.color =
//                         "#991b1b";

//                 } else if (
//                     totalStock <= threshold
//                 ) {

//                     stockBadge.textContent =
//                         "Low Stock";

//                     stockBadge.style.background =
//                         "#fef3c7";

//                     stockBadge.style.color =
//                         "#92400e";

//                 } else {

//                     stockBadge.textContent =
//                         "In Stock";

//                     stockBadge.style.background =
//                         "#dcfce7";

//                     stockBadge.style.color =
//                         "#166534";
//                 }
//             }
//         }
//     );
// }

/* =========================================================
   SEO SYSTEM
========================================================= */

function initSeoSystem() {
    const metaTitleInput = document.getElementById(
        "id_meta_title"
    );

    const metaDescriptionInput = document.getElementById(
        "id_meta_description"
    );

    const slugInput = document.getElementById(
        "id_slug"
    );

    const titleCounter = document.getElementById(
        "metaTitleCounter"
    );

    const descriptionCounter = document.getElementById(
        "metaDescriptionCounter"
    );

    const previewTitle = document.getElementById(
        "seoPreviewTitle"
    );

    const previewDescription = document.getElementById(
        "seoPreviewDescription"
    );

    const previewUrl = document.getElementById(
        "seoPreviewUrl"
    );

    const seoScoreValue = document.getElementById(
        "seoScoreValue"
    );

    const seoTitleStatus = document.getElementById(
        "seoTitleStatus"
    );

    const seoDescriptionStatus = document.getElementById(
        "seoDescriptionStatus"
    );

    function updateSeoInsights() {
        const title =
            metaTitleInput?.value || "";

        const description =
            metaDescriptionInput?.value || "";

        const slug =
            slugInput?.value || "";

        if (titleCounter) {
            titleCounter.textContent =
                `${title.length} / 60`;
        }

        if (descriptionCounter) {
            descriptionCounter.textContent =
                `${description.length} / 160`;
        }

        if (previewTitle) {
            previewTitle.textContent =
                title || "Product Meta Title Preview";
        }

        if (previewDescription) {
            previewDescription.textContent =
                description ||
                "Your SEO meta description preview will appear here automatically.";
        }

        if (previewUrl) {
            previewUrl.textContent =
                `https://example.com/products/${slug}`;
        }

        if (seoTitleStatus) {
            if (title.length >= 50 &&
                title.length <= 60) {

                seoTitleStatus.textContent =
                    "Optimized";
            } else if (title.length > 0) {
                seoTitleStatus.textContent =
                    "Needs Improvement";
            } else {
                seoTitleStatus.textContent =
                    "Empty";
            }
        }

        if (seoDescriptionStatus) {
            if (
                description.length >= 140 &&
                description.length <= 160
            ) {
                seoDescriptionStatus.textContent =
                    "Optimized";
            } else if (description.length > 0) {
                seoDescriptionStatus.textContent =
                    "Needs Improvement";
            } else {
                seoDescriptionStatus.textContent =
                    "Empty";
            }
        }

        let score = 0;
        if (
            title.length >= 50 &&
            title.length <= 60
        ) {
            score += 50;
        }

        if (
            description.length >= 140 &&
            description.length <= 160
        ) {
            score += 50;
        }

        if (seoScoreValue) {
            seoScoreValue.textContent =
                `${score}%`;
        }
    }

    [
        metaTitleInput,
        metaDescriptionInput,
        slugInput
    ].forEach((input) => {
        if (!input) {
            return;
        }

        input.addEventListener(
            "input",
            updateSeoInsights
        );
    });

    updateSeoInsights();

}

/* =========================================================
   PRODUCT SIDEBAR SYSTEM
========================================================= */

function initProductSidebar() {
    const statusSelect = document.getElementById(
        "id_status"
    );

    const statusBadge = document.getElementById(
        "productStatusBadge"
    );

    const statusMessage = document.getElementById(
        "productStatusMessage"
    );

    const seoScore = document.getElementById(
        "seoScoreValue"
    );

    const sidebarSeoScore = document.getElementById(
        "sidebarSeoScore"
    );

    function updateProductStatus() {
        if (
            !statusSelect ||
            !statusBadge ||
            !statusMessage
        ) {
            return;
        }

        const status =
            statusSelect.value;

        if (status === "draft") {
            statusBadge.textContent =
                "Draft";

            statusBadge.style.background =
                "#fef3c7";

            statusBadge.style.color =
                "#92400e";

            statusMessage.textContent =
                "This product is currently saved as draft.";
        }

        else if (
            status === "published"
        ) {
            statusBadge.textContent =
                "Published";

            statusBadge.style.background =
                "#dcfce7";

            statusBadge.style.color =
                "#166534";

            statusMessage.textContent =
                "This product is live and visible to customers.";
        }

        else {
            statusBadge.textContent =
                "Archived";

            statusBadge.style.background =
                "#fee2e2";

            statusBadge.style.color =
                "#991b1b";

            statusMessage.textContent =
                "This product has been archived.";
        }
    }

    function syncSeoScore() {
        if (
            seoScore &&
            sidebarSeoScore
        ) {
            sidebarSeoScore.textContent =
                seoScore.textContent;
        }
    }

    if (statusSelect) {
        statusSelect.addEventListener(
            "change",
            updateProductStatus
        );
    }

    if (seoScore) {
        const observer =
            new MutationObserver(
                syncSeoScore
            );

        observer.observe(
            seoScore,
            {
                childList: true,
            }
        );
    }

    updateProductStatus();

    syncSeoScore();
}

/* =========================================================
   BRAND AUTO SLUG
========================================================= */

function initBrandAutoSlug() {
    const brandName =
        document.getElementById(
            "id_name"
        );

    const brandSlug =
        document.getElementById(
            "id_slug"
        );

    if (
        !brandName ||
        !brandSlug
    ) {
        return;
    }

    brandName.addEventListener(
        "input",
        function () {
            const slug =
                this.value
                    .toLowerCase()
                    .trim()
                    .replace(/[^\w\s-]/g, "")
                    .replace(/\s+/g, "-");

            brandSlug.value = slug;
        }
    );
}

/* =========================================================
   BRAND FILE PREVIEW
========================================================= */

function initBrandFilePreview() {
    const fileInput =
        document.getElementById(
            "id_logo"
        );

    if (!fileInput) {
        return;
    }

    fileInput.addEventListener(
        "change",
        function () {

            if (
                this.files &&
                this.files.length > 0
            ) {

                this.style.borderColor =
                    "#ec4899";
            }
        }
    );
}

/* =========================================================
   BRAND LOGO UPLOAD
========================================================= */

function initBrandLogoUpload() {
    const dropzone =
        document.getElementById(
            "brandLogoDropzone"
        );

    const input =
        document.getElementById(
            "id_logo"
        );

    const fileName =
        document.getElementById(
            "brandFileName"
        );

    const uploadButton =
    document.getElementById(
        "brandUploadButton"
    );

    if (
        !dropzone ||
        !input
    ) {
        return;
    }

    dropzone.addEventListener(
        "click",
        function (event) {

            /* Prevent double trigger */
            if (
                event.target.closest(
                    ".brand-upload-btn"
                )
            ) {
                return;
            }

            input.click();
        }
    );

    if (uploadButton) {
        uploadButton.addEventListener(
            "click",
            function (event) {
                event.stopPropagation();

                input.click();
            }
        );
    }

    input.addEventListener(
        "change",
        function () {
            if (
                this.files &&
                this.files.length > 0
            ) {
                fileName.textContent =
                    this.files[0].name;

                dropzone.classList.add(
                    "is-uploaded"
                );
            }
        }
    );
}

/* =========================================================
   BRAND SIDEBAR ACTIONS
========================================================= */

function initBrandSidebarActions() {
    const previewButton =
        document.querySelector(
            ".preview-brand-btn"
        );

    const duplicateButton =
        document.querySelector(
            ".duplicate-brand-btn"
        );

    if (previewButton) {
        previewButton.addEventListener(
            "click",
            function () {
                const slugInput =
                    document.getElementById(
                        "id_slug"
                    );

                if (
                    slugInput &&
                    slugInput.value.trim()
                ) {
                    const previewUrl =
                        `/api/products/brands/${slugInput.value}/`;
                        // `/api/products/brands/{{ original.slug }}/`;
                        // `/brands/${slugInput.value}/`;

                    window.open(
                        previewUrl,
                        "_blank"
                    );

                } else {
                    alert(
                        "Please enter brand slug first."
                    );
                }
            }
        );
    }
}