const color = require("tailwindcss/colors");

module.exports = {
    future: {
        removeDeprecatedGapUtilities: true,
        purgeLayersByDefault: true,
    },
    purge: {
        enabled: true, //true for production build
        content: ["../**/templates/*.html", "../**/analisis_sentimen/templates/**/*.html"],
    },
    darkMode: "class", // or 'media' or 'class'
    theme: {
        fontFamily: {
            sans: ["cairo", "sans-serif"],
        },
        extend: {},
    },
    variants: {
        extend: {
            backgroundColor: ["checked", "disabled"],
            opacity: ["dark"],
            overflow: ["hover"],
        },
    },
    plugins: [],
};
