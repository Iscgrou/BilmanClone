import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { verifyCsrfToken } from 'src/lib/security'

export async function POST(request: Request) {
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

    const response = NextResponse.json(
      { message: 'Logged out successfully' },
      { status: 200 }
    )

    // Clear all auth-related cookies
    response.cookies.delete('token')
    response.cookies.delete('csrf_secret')

    return response
  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
}
