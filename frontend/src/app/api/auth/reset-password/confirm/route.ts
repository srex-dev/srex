import { NextResponse } from 'next/server'
import { hash } from 'bcryptjs'
import { verifyResetToken } from '../reset-password/route'

export async function POST(request: Request) {
  try {
    const { token, password } = await request.json()

    if (!token || !password) {
      return NextResponse.json(
        { message: 'Token and password are required' },
        { status: 400 }
      )
    }

    // Verify the token
    const email = verifyResetToken(token)
    if (!email) {
      return NextResponse.json(
        { message: 'Invalid or expired token' },
        { status: 400 }
      )
    }

    // Hash the new password
    const hashedPassword = await hash(password, 12)

    // TODO: Update the user's password in your database
    // This is where you would update the user's password in your database
    // For example:
    // await prisma.user.update({
    //   where: { email },
    //   data: { password: hashedPassword },
    // })

    return NextResponse.json(
      { message: 'Password has been reset successfully' },
      { status: 200 }
    )
  } catch (error) {
    console.error('Password reset confirmation error:', error)
    return NextResponse.json(
      { message: 'Failed to reset password' },
      { status: 500 }
    )
  }
} 