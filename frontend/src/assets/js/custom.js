// page or window load
import logo from "../../assets/image/logo/vastrika-logo.png";

export function pageLoader(text = "Curating your style...") {
    const loader = document.getElementById("loading");
    if (!loader) return;

    loader.innerHTML = `
        <div class="vastrika-loader-screen" role="status" aria-live="polite">
            <div class="vastrika-loader-bg-shape shape-1"></div>
            <div class="vastrika-loader-bg-shape shape-2"></div>

            <div class="vastrika-loader-center">
                <div class="vastrika-loader-orbit">
                    <span class="orbit-ring orbit-ring-1"></span>
                    <span class="orbit-ring orbit-ring-2"></span>

                    <span class="spark spark-1"></span>
                    <span class="spark spark-2"></span>
                    <span class="spark spark-3"></span>

                    <div class="vastrika-loader-logo-wrap">
                        <img src="${logo}" alt="Vastrika" class="vastrika-loader-logo" />
                    </div>
                </div>

                <h2 class="vastrika-loader-title">VASTRIKA</h2>
                <p class="vastrika-loader-text">${text}</p>

                <div class="vastrika-loader-bar">
                    <span></span>
                </div>
            </div>
        </div>
    `;

    loader.style.display = "block";
    loader.style.opacity = "1";

    setTimeout(() => {
        loader.style.transition = "opacity 0.5s ease";
        loader.style.opacity = "0";

        setTimeout(() => {
            loader.style.display = "none";
            loader.innerHTML = "";
        }, 500);
    }, 1800);
}