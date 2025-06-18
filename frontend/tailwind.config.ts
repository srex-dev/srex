import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: '#22313A',
        green: '#6CBF43',
        'green-dark': '#4A7C2C',
        red: '#E94F4F',
        cream: '#F3F3E6',
      },
      backgroundColor: {
        DEFAULT: '#22313A',
      },
    },
  },
  plugins: [],
};

export default config; 