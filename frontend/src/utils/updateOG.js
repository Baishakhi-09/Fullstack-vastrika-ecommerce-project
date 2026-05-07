// -------------------- HELPERS -------------------- //
const setMetaTag = (attr, name, content) => {
    if (!content) return;

    let element = document.querySelector(`meta[${attr}="${name}"]`);

    if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attr, name);
        document.head.appendChild(element);
    }

    element.setAttribute("content", content);
};

const setLinkTag = (rel, href) => {
    if (!href) return;

    let link = document.querySelector(`link[rel="${rel}"]`);

    if (!link) {
        link = document.createElement("link");
        link.setAttribute("rel", rel);
        document.head.appendChild(link);
    }

    link.setAttribute("href", href);
};

// -------------------- MAIN META -------------------- //
export const updateMeta = ({
    title,
    description,
    keywords,
    canonical,
    robots = "index, follow"
}) => {
    // Title
    if (title) document.title = title;

    // Basic SEO
    setMetaTag("name", "description", description);
    setMetaTag("name", "keywords", keywords);
    setMetaTag("name", "robots", robots);

    // Canonical URL (important for SEO)
    if (canonical) {
        setLinkTag("canonical", canonical);
    }
};

// -------------------- OPEN GRAPH + SOCIAL -------------------- //
export const updateOG = ({
    title,
    description,
    image,
    url,
    type = "website"
}) => {
    // Open Graph (Facebook, LinkedIn)
    setMetaTag("property", "og:title", title);
    setMetaTag("property", "og:description", description);
    setMetaTag("property", "og:image", image);
    setMetaTag("property", "og:url", url);
    setMetaTag("property", "og:type", type);

    // Twitter Cards (very important for sharing)
    setMetaTag("name", "twitter:card", "summary_large_image");
    setMetaTag("name", "twitter:title", title);
    setMetaTag("name", "twitter:description", description);
    setMetaTag("name", "twitter:image", image);
};