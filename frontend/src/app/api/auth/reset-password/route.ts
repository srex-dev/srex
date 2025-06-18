import { NextResponse } from 'next/server'
import { Resend } from 'resend'
import { createHash } from 'crypto'

// Initialize Resend with your API key
const resend = new Resend(process.env.RESEND_API_KEY)

// In-memory store for reset tokens (replace with database in production)
const resetTokens = new Map<string, { email: string; expires: number }>()

export async function POST(request: Request) {
  try {
    const { email } = await request.json()

    if (!email) {
      return NextResponse.json(
        { message: 'Email is required' },
        { status: 400 }
      )
    }

    // Generate a secure random token
    const token = createHash('sha256')
      .update(Math.random().toString())
      .digest('hex')

    // Store the token with expiration (1 hour)
    const expires = Date.now() + 3600000 // 1 hour
    resetTokens.set(token, { email, expires })

    // Send reset email
    await resend.emails.send({
      from: 'noreply@yourdomain.com',
      to: email,
      subject: 'Reset your password',
      html: `
        <p>Click the link below to reset your password:</p>
        <a href="${process.env.NEXTAUTH_URL}/auth/reset-password/${token}">
          Reset Password
        </a>
        <p>This link will expire in 1 hour.</p>
      `,
    })

    return NextResponse.json(
      { message: 'Password reset instructions sent' },
      { status: 200 }
    )
  } catch (error) {
    console.error('Password reset error:', error)
    return NextResponse.json(
      { message: 'Failed to send reset instructions' },
      { status: 500 }
    )
  }
}

// Helper function to verify reset token
export function verifyResetToken(token: string) {
  const resetData = resetTokens.get(token)
  if (!resetData) return null

  if (Date.now() > resetData.expires) {
    resetTokens.delete(token)
    return null
  }

  return resetData.email
} 