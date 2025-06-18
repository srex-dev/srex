import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Logo() {
  return (
    <Link href="/" className="flex items-center space-x-2">
      <div className="flex-shrink-0">
        <Image
          src="/srex-logo.png"
          alt="SREX Logo"
          width={48}
          height={48}
          priority
        />
      </div>
    </Link>
  );
} 