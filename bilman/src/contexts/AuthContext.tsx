'use client'

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  username: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string, rememberMe?: boolean) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [csrfToken, setCsrfToken] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    checkUser()
  }, [])

  const checkUser = async () => {
    try {
      const res = await fetch('/api/auth/me', {
        headers: {
          'x-csrf-token': csrfToken || '',
        },
        credentials: 'include',
      })
      if (res.ok) {
        const userData = await res.json()
        setUser(userData)
        setCsrfToken(userData.csrfToken)
      }
    } catch (error) {
      console.error('Error checking user:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string, rememberMe: boolean = false) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'x-csrf-token': csrfToken || '',
      },
      body: JSON.stringify({ username, password, rememberMe }),
      credentials: 'include',
    })

    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.message || 'Authentication failed')
    }

    const data = await res.json()
    setCsrfToken(data.csrfToken)
    setUser(data.user)
    router.push('/dashboard')
  }

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'x-csrf-token': csrfToken || '',
        },
        credentials: 'include',
      })
      setUser(null)
      setCsrfToken(null)
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
