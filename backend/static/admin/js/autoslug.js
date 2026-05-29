/* =========================================================
   PRODUCT TAG AUTO SLUG + AI ANALYSIS
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {
        const tagNameInput =
            document.querySelector(
                "#id_name"
            );

        const slugInput =
            document.querySelector(
                "#id_slug"
            );

        const descriptionInput =
            document.querySelector(
                "#id_description"
            );

        const nameCounter =
            document.querySelector(
                "#name-character-counter"
            );

        const descriptionCounter =
            document.querySelector(
                "#description-character-counter"
            );

        const validationFeedback =
            document.querySelector(
                "#name-validation-feedback"
            );

        const suggestedSlugText =
            document.querySelector(
                "#suggested-slug-text"
            );

        const seoScore =
            document.querySelector(
                "#description-seo-score"
            );

        function generateSlug(value) {
            return value
                .toLowerCase()
                .trim()
                .replace(
                    /[^\w\s-]/g,
                    ""
                )
                .replace(
                    /\s+/g,
                    "-"
                )
                .replace(
                    /--+/g,
                    "-"
                );
        }

        async function analyzeTag() {
            if (!tagNameInput) {
                return;
            }

            try {
                const title =
                    tagNameInput.value || "";

                const description =
                    descriptionInput?.value || "";

                const response =
                    await fetch(
                        `/api/products/ai-analysis/?title=${encodeURIComponent(title)}&description=${encodeURIComponent(description)}`
                    );

                if (!response.ok) {
                    throw new Error(
                        "AI analysis failed."
                    );
                }

                const data =
                    await response.json();

                const seoScoreValue =
                    document.querySelector(
                        "#seo-score-value"
                    );

                if (
                    seoScoreValue
                ){
                    seoScoreValue.textContent =
                        `${data.seo_score}%`;
                }

                const searchVisibility =
                    document.querySelector(
                        "#search-visibility"
                    );

                if (
                    searchVisibility
                ){
                    if(data.seo_score >= 80){

                        searchVisibility.textContent =
                            "High Visibility";

                    }

                    else if(data.seo_score >= 50){

                        searchVisibility.textContent =
                            "Medium Visibility";

                    }

                    else{

                        searchVisibility.textContent =
                            "Low Visibility";

                    }
                }

                const visibilityStatus =
                    document.querySelector(
                        "#visibility-status"
                    );

                if (
                    visibilityStatus
                ){
                    if(data.seo_score >= 80){

                        visibilityStatus.textContent =
                            "Optimized";

                    }

                    else if(data.seo_score >= 50){

                        visibilityStatus.textContent =
                            "Average";

                    }

                    else{

                        visibilityStatus.textContent =
                            "Needs Improvement";

                    }
                }

                const progressBar =
                    document.querySelector(
                        "#optimization-progress"
                    );

                if (
                    progressBar
                ){
                    progressBar.style.width =
                        `${data.seo_score}%`;

                    progressBar.dataset.progress =
                        data.seo_score;
                }

                if (
                    slugInput &&
                    data.slug
                ) {
                    slugInput.value =
                        data.slug;
                }

                if (
                    seoScore &&
                    data.seo_score !== undefined
                ) {
                    seoScore.textContent =
                        `SEO Score: ${data.seo_score}%`;
                }

                if (
                    suggestedSlugText
                ) {
                    suggestedSlugText.textContent =
                        data.slug ||
                        "product-tag";
                }
            }

            catch (error) {
                console.error(
                    "AI Analysis Error:",
                    error
                );
            }
        }

        let analysisTimeout;

        if (tagNameInput) {
            tagNameInput.addEventListener(
                "input",
                function () {
                    const value =
                        this.value || "";

                    if (nameCounter) {
                        nameCounter.textContent =
                            `${value.length} / 100`;
                    }

                    const generatedSlug =
                        generateSlug(
                            value
                        );

                    if (slugInput) {
                        slugInput.value =
                            generatedSlug;
                    }

                    if (
                        suggestedSlugText
                    ) {
                        suggestedSlugText.textContent =
                            generatedSlug ||
                            "product-tag";
                    }

                    if (
                        validationFeedback
                    ) {
                        if (
                            value.length < 3
                        ) {
                            validationFeedback.textContent =
                                "Too Short";

                            validationFeedback.style.color =
                                "#dc2626";
                        }

                        else {
                            validationFeedback.textContent =
                                "Looks Good";

                            validationFeedback.style.color =
                                "#15803d";
                        }
                    }

                    clearTimeout(
                        analysisTimeout
                    );

                    if (
                        value.length >= 3
                    ) {
                        analysisTimeout =
                            setTimeout(
                                analyzeTag,
                                500
                            );
                    }
                }
            );
        }

        if (descriptionInput) {

            descriptionInput.addEventListener(
                "input",
                function () {

                    if (
                        descriptionCounter
                    ) {

                        descriptionCounter.textContent =
                            `${this.value.length} / 500`;

                    }

                    clearTimeout(
                        analysisTimeout
                    );

                    analysisTimeout =
                        setTimeout(
                            analyzeTag,
                            500
                        );

                }
            );

        }

        document
            .querySelectorAll(
                ".summary-progress-bar"
            )
            .forEach(
                (bar) => {
                    const progress =
                        parseInt(
                            bar.dataset.progress || 0,
                            10
                        );

                    bar.style.width =
                        `${progress}%`;
                }
            );
            
        if (
            tagNameInput &&
            tagNameInput.value
        ){
            analyzeTag();
        }
    }
);