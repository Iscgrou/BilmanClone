"use client"

import { useTranslation } from "react-i18next"
import { Suspense } from "react"
import Link from "next/link"

function HomePage() {
  const { t } = useTranslation()

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-4">{t("welcomeMessage")}</h1>
      <Link href="/login">
        <button className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition">
          {t("loginButton")}
        </button>
      </Link>
    </main>
  )
}

// Wrap the component with Suspense for better loading handling
export default function Home() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HomePage />
    </Suspense>
  )
}
