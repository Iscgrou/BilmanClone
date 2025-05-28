import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'
import { verifyCsrfToken } from './lib/security'

interface JWTPayload {
  id: string
  username: string
  role: string
}

// Define route access based on roles
const routeAccess = {
  '/dashboard': ['ADMIN', 'OPERATOR', 'REPRESENTATIVE'],
  '/representatives': ['ADMIN', 'OPERATOR'],
  '/invoices': ['ADMIN', 'OPERATOR', 'REPRESENTATIVE'],
  '/accounting': ['ADMIN'],
  '/settings': ['ADMIN'],
}

const protectedRoutes = Object.keys(routeAccess)
const authRoutes = ['/login']
const publicRoutes = ['/api/auth/login']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public routes
  if (publicRoutes.includes(pathname)) {
    return NextResponse.next()
  }

  const token = request.cookies.get('token')?.value
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route))
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route))

  // If no token and trying to access protected route
  if (!token && isProtectedRoute) {
    const url = new URL('/login', request.url)
    url.searchParams.set('from', pathname)
    return NextResponse.redirect(url)
  }

  // If has token and trying to access auth routes
  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // For protected routes, verify token and check role-based access
  if (isProtectedRoute && token) {
    try {
      // Verify JWT token using jose (Edge Runtime compatible)
      const secret = new TextEncoder().encode(process.env.JWT_SECRET || 'fallback-secret')
      const { payload } = await jwtVerify(token, secret) as { payload: JWTPayload }

      // Check CSRF token for API routes
      if (pathname.startsWith('/api/')) {
        const csrfToken = request.headers.get('x-csrf-token')
        const csrfSecret = request.cookies.get('csrf_secret')?.value

        if (!csrfToken || !csrfSecret || !verifyCsrfToken(csrfSecret, csrfToken)) {
          return NextResponse.json(
            { message: 'Invalid CSRF token' },
            { status: 403 }
          )
        }
      }

      // Check role-based access
      const routeRoles = routeAccess[pathname as keyof typeof routeAccess]
      if (routeRoles && !routeRoles.includes(payload.role)) {
        // Redirect to dashboard if user doesn't have access
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }

      return NextResponse.next()
    } catch (error) {
      // If token is invalid, clear it and redirect to login
      const response = NextResponse.redirect(new URL('/login', request.url))
      response.cookies.delete('token')
      response.cookies.delete('csrf_secret')
      return response
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Match all protected routes and auth routes
    '/dashboard/:path*',
    '/representatives/:path*',
    '/invoices/:path*',
    '/accounting/:path*',
    '/settings/:path*',
    '/login',
    '/api/auth/:path*',
  ],
}
