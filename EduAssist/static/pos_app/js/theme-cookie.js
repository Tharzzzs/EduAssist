(function () {
    function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function applyThemeFromCookie() {
    const isDark = getCookie("dark_mode") === "1";

    const html = document.documentElement;
    const body = document.body;
    const logo = document.querySelector(".logo");

    if (isDark) {
        html.classList.add("dark");
        body.classList.add("dark");

        if (logo) logo.style.setProperty("color", "white", "important");

    } else {
        html.classList.remove("dark");
        body.classList.remove("dark");

        if (logo) logo.style.setProperty("color", "black", "important");
    }
}


    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", applyThemeFromCookie);
    } else {
        applyThemeFromCookie();
    }

    document.addEventListener("click", applyThemeFromCookie);
})();
