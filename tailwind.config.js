const colors = require("tailwindcss/colors");

module.exports = {
  purge: [],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      spacing: {
        "25vh": "25vh",
        "50vh": "50vh",
        "75vh": "75vh",
        "1/4": "25%",
        "1/2": "50%",
        "3/4": "75%",
        "1/3": "30%",
        "2/3": "60%",
        "3/5": "60%",
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
