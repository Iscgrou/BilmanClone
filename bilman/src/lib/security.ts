import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Generate CSRF token using Web Crypto API
export const generateCsrfToken = async () => {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  const secret = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
  const token = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
  return { secret, token }
}

// Verify CSRF token using constant-time comparison
export const verifyCsrfToken = (secret: string, token: string) => {
  if (!secret || !token) return false
  if (secret.length !== token.length) return false
  
  let result = 0
  for (let i = 0; i < secret.length; i++) {
    result |= secret.charCodeAt(i) ^ token.charCodeAt(i)
  }
  return result === 0
}

// Simple in-memory rate limiting (Note: This is a basic implementation)
const rateLimit = new Map<string, { count: number; resetTime: number }>()

// Rate limiting middleware for API routes
export const rateLimitMiddleware = async (request: NextRequest) => {
  const ip = request.headers.get('x-forwarded-for') || 'unknown'
  const now = Date.now()
  const windowMs = 15 * 60 * 1000 // 15 minutes
  const maxRequests = 5 // 5 requests per window

  const rateLimitInfo = rateLimit.get(ip) || { count: 0, resetTime: now + windowMs }

  if (now > rateLimitInfo.resetTime) {
    rateLimitInfo.count = 1
    rateLimitInfo.resetTime = now + windowMs
  } else {
    rateLimitInfo.count++
  }

  rateLimit.set(ip, rateLimitInfo)

  if (rateLimitInfo.count > maxRequests) {
    return NextResponse.json(
      { error: 'Too many requests, please try again later.' },
      { status: 429 }
    )
  }

  return null
}
