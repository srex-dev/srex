'use client'

import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { AuthProvider } from '@/config/auth'

interface SSOButtonProps {
  provider: AuthProvider
  name: string
  icon: string
  disabled?: boolean
}

export default function SSOButton({ provider, name, icon, disabled }: SSOButtonProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      await signIn(provider, { callbackUrl: '/' })
    } catch (error) {
      console.error('SSO error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getIcon = () => {
    switch (icon) {
      case 'google':
        return (
          <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
            <path
              d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"
              fill="#4285F4"
            />
          </svg>
        )
      case 'github':
        return (
          <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
              fill="#333"
            />
          </svg>
        )
      case 'microsoft':
        return (
          <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
            <path
              d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"
              fill="#0078D4"
            />
          </svg>
        )
      default:
        return null
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={disabled || loading}
      className={`w-full flex items-center justify-center px-4 py-2 border border-green shadow-sm text-sm font-medium rounded-md text-navy bg-cream hover:bg-green hover:text-cream focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green disabled:opacity-50 disabled:bg-red disabled:text-cream disabled:cursor-not-allowed transition-colors duration-150`}
    >
      {getIcon()}
      {loading ? 'Connecting...' : `Continue with ${name}`}
    </button>
  )
} 