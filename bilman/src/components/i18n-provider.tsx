"use client"

import { useEffect, useState } from "react"
import i18n from "i18next"
import { initReactI18next } from "react-i18next"

const resources = {
  fa: {
    translation: {
      welcomeMessage: "به برنامه مدیریت فروش VPN خوش آمدید!",
      loginButton: "ورود",
      username: "نام کاربری",
      password: "رمز عبور",
      loginError: "خطایی رخ داده است. لطفا دوباره تلاش کنید.",
      loginSuccess: "ورود موفقیت‌آمیز",
      invalidCredentials: "نام کاربری یا رمز عبور اشتباه است.",
      serverError: "خطای سرور"
    }
  }
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    const initI18n = async () => {
      try {
        if (!i18n.isInitialized) {
          await i18n
            .use(initReactI18next)
            .init({
              resources,
              lng: "fa",
              fallbackLng: "fa",
              interpolation: {
                escapeValue: false
              },
              react: {
                useSuspense: false
              }
            })
        }
        setIsInitialized(true)
      } catch (error) {
        console.error("Failed to initialize i18n:", error)
        setIsInitialized(true) // Still render content even if i18n fails
      }
    }

    initI18n()
  }, [])

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    )
  }

  return children
}
