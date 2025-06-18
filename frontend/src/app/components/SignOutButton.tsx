'use client'

import { signOut } from 'next-auth/react'

export default function SignOutButton() {
  return (
    <button
      onClick={() => signOut()}
      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-gray-900 bg-green hover:bg-navy hover:text-green focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green transition-colors duration-150"
    >
      Sign out
    </button>
  )
} 