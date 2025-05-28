import { NextResponse } from 'next/server'
import { jwtVerify } from 'jose'
import { cookies } from 'next/headers'
import { prisma } from 'src/lib/prisma'
import { verifyCsrfToken, generateCsrfToken } from 'src/lib/security'

export async function GET(request: Request) {
  try {
    // Verify CSRF token
    const csrfToken = request.headers.get('x-csrf-token')
    const cookieStore = await cookies()
    const csrfSecret = cookieStore.get('csrf_secret')?.value

    if (!csrfToken || !csrfSecret || !verifyCsrfToken(csrfSecret, csrfToken)) {
      return NextResponse.json(
        { message: 'Invalid CSRF token' },
        { status: 403 }
      )
    }

    const token = cookieStore.get('token')?.value

    if (!token) {
      return NextResponse.json(
        { message: 'Not authenticated' },
        { status: 401 }
      )
    }

    // Verify JWT token using jose
    const secret = new TextEncoder().encode(process.env.JWT_SECRET || 'fallback-secret')
    const { payload } = await jwtVerify(token, secret)

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { id: payload.id as string },
      select: {
        id: true,
        username: true,
        role: true,
        createdAt: true,
        updatedAt: true,
      },
    })

    if (!user) {
      return NextResponse.json(
        { message: 'User not found' },
        { status: 404 }
      )
    }

    // Generate new CSRF token
    const { secret: newSecret, token: newCsrfToken } = await generateCsrfToken()

    const response = NextResponse.json({
      ...user,
      csrfToken: newCsrfToken,
    })

    // Update CSRF secret cookie
    response.cookies.set('csrf_secret', newSecret, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
    })

    return response
  } catch (error) {
    console.error('Auth check error:', error)
    return NextResponse.json(
      { message: 'Authentication failed' },
      { status: 401 }
    )
  }
}
