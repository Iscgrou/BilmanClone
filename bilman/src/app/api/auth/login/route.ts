import { NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { prisma } from 'src/lib/prisma'
import { SignJWT } from 'jose'
import { generateCsrfToken, verifyCsrfToken, rateLimitMiddleware } from 'src/lib/security'

export async function POST(request: Request) {
  // Check rate limiting
  const rateLimitResponse = await rateLimitMiddleware(request as any)
  if (rateLimitResponse) return rateLimitResponse

  // Verify CSRF token
  const csrfToken = request.headers.get('x-csrf-token')
  const csrfSecret = request.headers.get('x-csrf-secret')

  if (!csrfToken || !csrfSecret || !verifyCsrfToken(csrfSecret, csrfToken)) {
    return NextResponse.json(
      { message: 'Invalid CSRF token' },
      { status: 403 }
    )
  }

  try {
    const { username, password, rememberMe } = await request.json()

    const user = await prisma.user.findUnique({
      where: { username },
    })

    if (!user) {
      return NextResponse.json(
        { message: 'Invalid credentials' },
        { status: 401 }
      )
    }

    const isValidPassword = await bcrypt.compare(password, user.password)

    if (!isValidPassword) {
      return NextResponse.json(
        { message: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Create JWT token with dynamic expiration using jose
    const secret = new TextEncoder().encode(process.env.JWT_SECRET || 'fallback-secret')
    const expiresIn = rememberMe ? '30d' : '1d'
    const token = await new SignJWT({ 
      id: user.id, 
      username: user.username,
      role: user.role 
    })
      .setProtectedHeader({ alg: 'HS256' })
      .setExpirationTime(expiresIn)
      .sign(secret)

    // Generate new CSRF token for the session
    const { secret: newSecret, token: newCsrfToken } = await generateCsrfToken()

    const response = NextResponse.json(
      { 
        message: 'Login successful',
        csrfToken: newCsrfToken,
        user: {
          id: user.id,
          username: user.username,
          role: user.role
        }
      },
      { status: 200 }
    )

    // Set cookies
    const maxAge = rememberMe ? 30 * 24 * 60 * 60 : 24 * 60 * 60 // 30 days or 1 day
    
    response.cookies.set('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge,
      path: '/',
    })

    response.cookies.set('csrf_secret', newSecret, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge,
      path: '/',
    })

    return response
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
}
