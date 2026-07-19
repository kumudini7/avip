import withMT from '@material-tailwind/react/utils/withMT';

/** @type {import('tailwindcss').Config} */
export default withMT({
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        avip: {
          50: '#eefaf7',
          100: '#d6f3eb',
          200: '#abe7d4',
          300: '#72d5b4',
          400: '#3ebd91',
          500: '#21936f',
          600: '#1a7357',
          700: '#165c47',
          800: '#14493a',
          900: '#123d31',
        },
      },
      boxShadow: {
        soft: '0 18px 50px rgba(15, 23, 42, 0.10)',
      },
    },
  },
  plugins: [],
});
