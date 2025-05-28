import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
// Import translation files
const translationFA = {
  "welcomeMessage": "به برنامه مدیریت فروش VPN خوش آمدید!",
  "loginButton": "ورود"
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      fa: {
        translation: translationFA,
      },
    },
    lng: 'fa',
    fallbackLng: 'fa',
    interpolation: {
      escapeValue: false,
    },
    react: {
      useSuspense: false,
    },
  });

export default i18n;
