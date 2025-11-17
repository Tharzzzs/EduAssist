
(function () {
    function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function applyThemeFromCookie() {
        const v = getCookie("dark_mode");
        const isDark = v === "1";
        if (isDark) {
            document.documentElement.classList.add("dark");
            document.body.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
            document.body.classList.remove("dark");
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", applyThemeFromCookie);
    } else {
        applyThemeFromCookie();
    }
})();
