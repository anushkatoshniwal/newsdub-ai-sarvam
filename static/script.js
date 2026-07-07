/**
 * NewsDub AI — frontend logic (vanilla JavaScript)
 */

(function () {
    "use strict";

    // --- DOM elements ---
    const headlinesList = document.getElementById("headlines-list");
    const headlinesLoading = document.getElementById("headlines-loading");
    const headlinesError = document.getElementById("headlines-error");
    const refreshBtn = document.getElementById("refresh-btn");

    const articleEmpty = document.getElementById("article-empty");
    const articleContent = document.getElementById("article-content");
    const articleTitle = document.getElementById("article-title");
    const articleSummary = document.getElementById("article-summary");
    const articleLink = document.getElementById("article-link");

    const dubForm = document.getElementById("dub-form");
    const languageSelect = document.getElementById("language-select");
    const dubBtn = document.getElementById("dub-btn");
    const dubLoading = document.getElementById("dub-loading");
    const dubLoadingText = document.getElementById("dub-loading-text");
    const dubError = document.getElementById("dub-error");
    const dubResult = document.getElementById("dub-result");
    const translatedText = document.getElementById("translated-text");
    const audioPlayer = document.getElementById("audio-player");
    const downloadLink = document.getElementById("download-link");

    // --- App state ---
    let headlines = [];
    let selectedHeadline = null;

    /**
     * Show or hide an element.
     */
    function toggle(el, show) {
        el.hidden = !show;
    }

    /**
     * Fetch JSON from an API route and handle errors.
     */
    async function fetchJSON(url, options) {
        const response = await fetch(url, options);
        const data = await response.json().catch(function () {
            return { success: false, error: "Invalid server response." };
        });

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Request failed.");
        }

        return data;
    }

    /**
     * Load headlines from the backend.
     */
    async function loadHeadlines() {
        toggle(headlinesLoading, true);
        toggle(headlinesError, false);
        headlinesList.innerHTML = "";

        try {
            const data = await fetchJSON("/api/headlines?limit=5");
            headlines = data.headlines;
            renderHeadlines();
        } catch (err) {
            headlinesError.textContent = err.message;
            toggle(headlinesError, true);
        } finally {
            toggle(headlinesLoading, false);
        }
    }

    /**
     * Render the headline list.
     */
    function renderHeadlines() {
        headlinesList.innerHTML = "";

        headlines.forEach(function (headline, index) {
            const li = document.createElement("li");
            li.className = "headline-item";

            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "headline-btn";
            btn.dataset.id = headline.id;

            if (selectedHeadline && selectedHeadline.id === headline.id) {
                btn.classList.add("is-selected");
            }

            btn.innerHTML =
                '<span class="headline-btn__index">' +
                (index + 1) +
                ".</span>" +
                escapeHTML(headline.title);

            btn.addEventListener("click", function () {
                selectHeadline(headline);
            });

            li.appendChild(btn);
            headlinesList.appendChild(li);
        });
    }

    /**
     * Escape HTML to prevent XSS when inserting user-facing strings.
     */
    function escapeHTML(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Select a headline and show its details.
     */
    function selectHeadline(headline) {
        selectedHeadline = headline;

        articleTitle.textContent = headline.title;
        articleSummary.textContent = headline.summary;
        articleLink.href = headline.link || "#";
        articleLink.style.display = headline.link ? "inline" : "none";

        toggle(articleEmpty, false);
        toggle(articleContent, true);

        dubBtn.disabled = !languageSelect.value;
        resetDubResult();

        renderHeadlines();
    }

    /**
     * Clear translation and audio results.
     */
    function resetDubResult() {
        toggle(dubResult, false);
        toggle(dubError, false);
        translatedText.textContent = "";
        audioPlayer.removeAttribute("src");
        audioPlayer.load();
        downloadLink.removeAttribute("href");
    }

    /**
     * Translate the selected headline and generate speech.
     */
    async function handleDubSubmit(event) {
        event.preventDefault();

        if (!selectedHeadline) {
            dubError.textContent = "Please select a headline first.";
            toggle(dubError, true);
            return;
        }

        const targetLanguage = languageSelect.value;
        if (!targetLanguage) {
            dubError.textContent = "Please choose a language.";
            toggle(dubError, true);
            return;
        }

        resetDubResult();
        toggle(dubLoading, true);
        dubBtn.disabled = true;
        dubLoadingText.textContent = "Translating…";

        try {
            const translateData = await fetchJSON("/api/translate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: selectedHeadline.title,
                    summary: selectedHeadline.summary,
                    target_language: targetLanguage,
                }),
            });

            translatedText.textContent = translateData.translated_text;
            translatedText.lang = targetLanguage.split("-")[0];
            toggle(dubResult, true);

            dubLoadingText.textContent = "Generating audio…";

            const ttsData = await fetchJSON("/api/synthesize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: translateData.translated_text,
                    target_language: targetLanguage,
                }),
            });

            const audioUrl = ttsData.audio_url;
            audioPlayer.src = audioUrl;
            downloadLink.href = audioUrl;
            downloadLink.download = ttsData.filename || "newsdub-audio.wav";

            audioPlayer.load();
            audioPlayer.play().catch(function () {
                /* Autoplay may be blocked; user can press play manually. */
            });
        } catch (err) {
            dubError.textContent = err.message;
            toggle(dubError, true);
        } finally {
            toggle(dubLoading, false);
            dubBtn.disabled = !selectedHeadline || !languageSelect.value;
        }
    }

    // --- Event listeners ---
    refreshBtn.addEventListener("click", loadHeadlines);

    languageSelect.addEventListener("change", function () {
        dubBtn.disabled = !selectedHeadline || !languageSelect.value;
    });

    dubForm.addEventListener("submit", handleDubSubmit);

    // --- Init ---
    loadHeadlines();
})();
