/** @type {import('tailwindcss').Config} */
const tailwindCSSAnimista =require("tailwindcss-animistacss")
const animista__defaults = require('tailwindcss-animistacss/animista__defaults')
module.exports = {
  content:["./templates/*html"],
  theme: {
    extend: {
      colors:{
        'beige':'rgb(247, 200, 224)',
        'gr':'rgb(70,26,89)'
      },
      height:{
        'ext':'1000px',
        'per':'130rem'
      },
      width:{
        'ext':'55rem',
      },
      fontFamily:{
        'body':['Pacifico','cursive'],
        'quotes':['Great Vibes','cursive'],
        'div':['Roboto Condensed','sans-serif']
      },
      letterSpacing:{
        'rombha':'0.25rem'
      }
    }
  },
  plugins: [
    tailwindCSSAnimista({
      classes:['animate__tracking-in-expand','animate__scale-up-tl','animate__scale-up-tr','animate__focus-in-contract-bck','animate__swing-in-left-fwd'],
      settings:{
        'animate__tracking-in-expand':{
          duration:500,
          delay:1,
          iterationCounts:1,
          isInfinite:false,
        },
        'animate__scale-up-tl':{
          duration:1000,
          delay:10,
          iterationCounts:1,
          isInfinite:false,
        },
        'animate__scale-up-tr':{
          duration:1000,
          delay:400,
          iterationCounts:1,
          isInfinite:false,
        },
        'animate__focus-in-contract-bck':{
          duration:5000,
          delay:1,
          iterationCounts:3,
          isInfinite:false,
        },
        'animate__swing-in-left-fwd':{
          duration:5000,
          delay:5,
          iterationCounts:1,
          isInfinite:false,
        },
      },
      variants:["responsive"]
    })
  ],
}

