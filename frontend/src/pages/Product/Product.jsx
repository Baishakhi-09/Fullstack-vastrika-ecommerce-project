import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";

const PRODUCTS_API = 
    import.meta.env.VITE_PRODUCTS_API || "http://127.0.0.1:8000/api/products";

const formatDateLocal = (date) => {
    return new Date(date).toLocaleString(undefined, {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZoneName: "short",
    });
};

const timeAgo = (date) => {
    const now = new Date();
    const past = new Date(date);
    const seconds = Math.floor((now - past) / 1000);

    if (seconds < 60) return "Just now";

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} min ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hr ago`;

    const days = Math.floor(hours / 24);
    if (days < 7) return `${days} day${days > 1 ? "s" : ""} ago`;

    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `${weeks} week${weeks > 1 ? "s" : ""} ago`;

    const months = Math.floor(days / 30);
    if (months < 12) return `${months} month${months > 1 ? "s" : ""} ago`;

    const years = Math.floor(days / 365);
    return `${years} year${years > 1 ? "s" : ""} ago`;
};

const SORT_OPTIONS = [
    { value: "newest", label: "Newest" },
    { value: "price_low_to_high", label: "Price: Low to High" },
    { value: "price_high_to_low", label: "Price: High to Low" },
    { value: "rating", label: "Top Rated" },
    { value: "discount", label: "Best Discount" },
    { value: "name_asc", label: "Name A-Z" },
    { value: "name_desc", label: "Name Z-A" },
];

const initialFilters = {
    q: "",
    category: "",
    brand: "",
    gender: "",
    size: "",
    color: "",
    min_price: "",
    max_price: "",
    sort: "newest",
    page: 1,
};

function useQueryParams() {
    const location = useLocation();
    return useMemo(() => new URLSearchParams(location.search), [location.search]);
}

function ProductCard({ product }) {
    const [hovered, setHovered] = useState(false);

    const imageToShow =
     hovered && product.hover_image ? product.hover_image : product.primary_image;

    return (
        <Link
        to={`/product/${product.slug}`}
        className="plp-card"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}>
            <div className="plp-card-image-wrap">
                {imageToShow ? (
                    <img src={imageToShow} alt={product.name} className="plp-card-image" loading="lazy" />
                ) : (
                    <div className="plp-card-no-image">No Image</div>
                )}

                {product.is_new_arrival && <span className="plp-badge">New</span>}
            </div>

            <div className="plp-card-body">
                <h4 className="plp-brand">{product.brand || "Brand"}</h4>
                <p className="plp-name">{product.name}</p>

                <p className="plp-date">
                    {timeAgo(product.created_at)} • {formatDateLocal(product.created_at)}
                </p>

                <div className="plp-rating-row">
                    <span className="plp-rating">
                        {Number(product.average_rating || 0).toFixed(1)} ★
                    </span>
                    <span className="plp-review-count">({product.review_count || 0})</span>
                </div>

                <div className="plp-price-row">
                    <span className="plp-price">₹{product.selling_price}</span>
                    <span className="plp-mrp">₹{product.mrp}</span>
                    <span className="plp-discount">({product.discount_percent}% OFF)</span>
                </div>

                {product.available_sizes?.length > 0 && (
                    <div className="plp-sizes">
                        {product.available_sizes.slice(0, 5).map((size) => (
                            <span key={size} className="plp-size-chip">
                                {size}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </Link>
    );
}

function FilterSidebar({
    filterMeta,
    filters,
    onChange,
    onReset,
    mobileOpen,
    setMobileOpen,
}) {
    return (
        <>
            <div className={`plp-mobile-backdrop ${mobileOpen ? "show" : ""}`} onClick={() => setMobileOpen(false)} />
            <aside className={`plp-sidebar ${mobileOpen ? "open" : ""}`}>
                <div className="plp-sidebar-top">
                    <h3>Filters</h3>
                    <button type="button" className="plp-reset-btn" onClick={onReset}>
                        Clear All
                    </button>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="search">Search</label>
                    <input type="text" value={filters.q} onChange={(e) => onChange("q", e.target.value)} id="search" name="search" placeholder="Search products..." />
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="category">Category</label>
                    <select id="category" name="category" value={filters.category} onChange={(e) => onChange("category", e.target.value)}>
                        <option value="">All Categories</option>
                        {filterMeta.categories?.map((item) => (
                            <option key={item.id} value={item.slug}>
                                {item.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="brand">Brand</label>
                    <select id="brand" name="brand" value={filters.brand} onChange={(e) => onChange("brand", e.target.value)}>
                        <option value="">All Brands</option>
                        {filterMeta.brands?.map((item) => (
                            <option key={item.id} value={item.slug}>
                                {item.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="gender">Gender</label>
                    <select id="gender" name="gender" value={filters.gender} onChange={(e) => onChange("gender", e.target.value)}>
                        <option value="">All</option>
                        <option value="men">Men</option>
                        <option value="women">Women</option>
                        <option value="kids">Kids</option>
                        <option value="unisex">Unisex</option>
                    </select>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="size">Size</label>
                    <select id="size" name="size" value={filters.size} onChange={(e) => onChange("size", e.target.value)}>
                        <option value="">All Sizes</option>
                        {filterMeta.sizes?.map((item) => (
                            <option key={item} value={item}>
                                {item}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="color">Color</label>
                    <select id="color" name="color" value={filters.color} onChange={(e) => onChange("color", e.target.value)}>
                        <option value="">All Colors</option>
                        {filterMeta.colors?.map((item) => (
                            <option key={item} value={item}>
                                {item}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="min_price">Min Price</label>
                    <input id="min_price" name="min_price" type="number" value={filters.min_price} onChange={(e) => onChange("min_price", e.target.value)} placeholder="0" />
                </div>

                <div className="plp-filter-group">
                    <label htmlFor="max_price">Max Price</label>
                    <input id="max_price" name="max_price" type="number" value={filters.max_price} onChange={(e) => onChange("max_price", e.target.value)} placeholder="5000" />
                </div>

                <button type="button" className="plp-apply-mobile-btn" onClick={() => setMobileOpen(false)}>
                    Apply Filters
                </button>
            </aside>
        </>
    );
}

function Pagination({ currentPage, totalPages, onPageChange }) {
    if (totalPages <= 1) return null;

    const pages = [];
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, currentPage + 2);

    for (let i = start; i <= end; i += 1) {
        pages.push(i);
    }

    return (
        <div className="plp-pagination">
            <button type="button" disabled={currentPage === 1} onClick={() => onPageChange(currentPage - 1)}>
                Prev
            </button>

            {pages.map((page) => (
                <button type="button" key={page} className={page === currentPage ? "active" : ""} onClick={() => onPageChange(page)}>
                    {page}
                </button>
            ))}

            <button type="button" disabled={currentPage === totalPages} onClick={() => onPageChange(currentPage + 1)}>
                Next
            </button>
        </div>
    );
}

export default function Product() {
    const { departmentSlug, sectionSlug, itemSlug } = useParams();

    const navigate = useNavigate();
    const queryParams = useQueryParams();

    const [filters, setFilters] = useState(initialFilters);
    const [products, setProducts] = useState([]);
    const [count, setCount] = useState(0);
    const [pageSize] = useState(20);
    const [loading, setLoading] = useState(true);
    const [metaLoading, setMetaLoading] = useState(true);
    const [error, setError] = useState("");
    const [filterMeta, setFilterMeta] = useState({
        categories: [],
        brands: [],
        sizes: [],
        colors: [],
        tags: [],
    });
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        const next = {
            q: queryParams.get("q") || "",
            category: queryParams.get("category") || "",
            brand: queryParams.get("brand") || "",
            gender: queryParams.get("gender") || "",
            size: queryParams.get("size") || "",
            color: queryParams.get("color") || "",
            min_price: queryParams.get("min_price") || "",
            max_price: queryParams.get("max_price") || "",
            sort: queryParams.get("sort") || "newest",
            page: Number(queryParams.get("page") || 1),
        };

        setFilters(next);
    }, [queryParams]);

    useEffect(() => {
        fetchFilterMeta();
    }, []);

    useEffect(() => {
        fetchProducts();
    }, [filters, departmentSlug, sectionSlug, itemSlug]);

    const totalPages = Math.ceil(count / pageSize);

    const buildBasePath = () => {
        return ["/products", departmentSlug, sectionSlug, itemSlug]
         .filter(Boolean)
         .join("/");
    };

    const updateURL = (nextFilters) => {
        const params = new URLSearchParams();

        Object.entries(nextFilters).forEach(([key, value]) => {
            if (value !== "" && value !== null && value !== undefined) {
                params.set(key, value);
            }
        });

        navigate(`${buildBasePath()}?${params.toString()}`);
    };

    const handleFilterChange = (key, value) => {
        const next = {
            ...filters,
            [key]: value,
            page: key === "page" ? value : 1,
        };
        updateURL(next);
    };

    const handleResetFilters = () => {
        navigate(buildBasePath());
        setFilters(initialFilters);
    };

    // FILTER API
    const fetchFilterMeta = async () => {
        setMetaLoading(true);
        try {
            const filterRes = await fetch(`${PRODUCTS_API}/filters/`);
            // const filterData = await filterRes.json();
            if (!filterRes.ok) throw new Error("Failed to load filters");

            const filterData = await filterRes.json();
            setFilterMeta(filterData);
        } catch (err) {
            console.error(err);
        } finally {
            setMetaLoading(false);
        }
    };

    // PRODUCT API
    const fetchProducts = async () => {
        setLoading(true);
        setError("");

        try {
            const params = new URLSearchParams();

             Object.entries(filters).forEach(([key, value]) => {
                if (value !== "" && value !== null && value !== undefined) {
                params.append(key, value);
                }
            });

            if (departmentSlug) params.append("department", departmentSlug);
            if (sectionSlug) params.append("section", sectionSlug);
            if (itemSlug) params.append("subcategory", itemSlug);

            const query = params.toString();
            const url = query ? `${PRODUCTS_API}/?${query}` : `${PRODUCTS_API}/`;

            const productRes = await fetch(url);
            
            if (!productRes.ok) {
                throw new Error("Failed to fetch products.");
            }

            const productData = await productRes.json();

            setProducts(productData.results || []);
            setCount(productData.count || 0);
        } catch (err) {
            console.error(err);
            setError("Unable to load products. Please try again.");
        } finally {
            setLoading(false);
        }
    };

  return (
    <section className="plp-page">
        <div className="plp-container">
            <div className="plp-header">
                <div>
                    <h1>Products</h1>
                    <p>
                        Discover premium styles, curated like a modern fashion marketplace.
                    </p>
                </div>

                <div className="plp-toolbar">
                    <button type="button" className="plp-mobile-filter-btn" onClick={() => setMobileOpen(true)}>
                        Filters
                    </button>

                    <select value={filters.sort} id="sort" name="sort"
                    onChange={(e) => handleFilterChange("sort", e.target.value)} className="plp-sort">
                        {SORT_OPTIONS.map((item) => (
                            <option key={item.value} value={item.value}>
                                Sort: {item.label}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="plp-result-bar">
                <span>{loading ? "Loading..." : `${count} items found`}</span>
            </div>

            <div className="plp-layout">
                <FilterSidebar filterMeta={filterMeta} filters={filters} onChange={handleFilterChange} onReset={handleResetFilters} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

                <div className="plp-main">
                    {metaLoading && <div className="plp-note">Loading filters...</div>}

                    {error && <div className="plp-error">{error}</div>}

                    {!loading && !error && products.length === 0 && (
                        <div className="plp-empty">
                            <h3>No products found</h3>
                            <p>Try changing your filters or search keyword.</p>
                            <button type="button" onClick={handleResetFilters}>
                                Reset Filters
                            </button>
                        </div>
                    )}

                    {loading ? (
                        <div className="plp-grid">
                            {Array.from({ length: 8 }).map((_, index) => (
                                <div className="plp-skeleton-card" key={index}>
                                    <div className="plp-skeleton-image" />
                                    <div className="plp-skeleton-line short" />
                                    <div className="plp-skeleton-line" />
                                    <div className="plp-skeleton-line medium" />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <>
                            <div className="plp-grid">
                                {products.map((product) => (
                                    <ProductCard key={product.id} product={product} />
                                ))}
                            </div>

                            <Pagination currentPage={filters.page} totalPages={totalPages} onPageChange={(page) => handleFilterChange("page", page)} />
                        </>
                    )}
                </div>
            </div>
        </div>
    </section>
  );
}
