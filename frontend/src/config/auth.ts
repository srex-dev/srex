import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import MicrosoftProvider from 'next-auth/providers/azure-ad';
import bcrypt from 'bcryptjs';

// This is a temporary user store. In a real application, you would use a database.
const users = [
  {
    id: '1',
    name: 'Admin User',
    email: 'admin@example.com',
    password: bcrypt.hashSync('admin123', 10),
    role: 'admin',
  },
];

export const authConfig = {
  providers: {
    google: {
      enabled: process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET,
      name: 'Google',
      icon: 'google',
    },
    github: {
      enabled: process.env.GITHUB_ID && process.env.GITHUB_SECRET,
      name: 'GitHub',
      icon: 'github',
    },
    microsoft: {
      enabled: process.env.MICROSOFT_CLIENT_ID && process.env.MICROSOFT_CLIENT_SECRET,
      name: 'Microsoft',
      icon: 'microsoft',
    },
  },
  session: {
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
    signOut: '/auth/signout',
    verifyRequest: '/auth/verify-request',
    newUser: '/auth/new-user',
  },
} as const;

export type AuthProvider = keyof typeof authConfig.providers;

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const user = users.find((user) => user.email === credentials.email);

        if (!user) {
          return null;
        }

        const isPasswordValid = await bcrypt.compare(credentials.password, user.password);

        if (!isPasswordValid) {
          return null;
        }

        return {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
        };
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_ID || '',
      clientSecret: process.env.GITHUB_SECRET || '',
    }),
    MicrosoftProvider({
      clientId: process.env.MICROSOFT_CLIENT_ID || '',
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET || '',
      tenantId: process.env.MICROSOFT_TENANT_ID,
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.role = user.role;
      }
      if (account) {
        token.provider = account.provider;
      }
      return token;
    },
    async session({ session, token }) {
      if (session?.user) {
        session.user.role = token.role;
        session.user.provider = token.provider;
      }
      return session;
    },
    async signIn({ user, account, profile }) {
      // Here you would typically:
      // 1. Check if the user exists in your database
      // 2. If not, create a new user
      // 3. Link the SSO account to the user
      // For now, we'll just allow all sign-ins
      return true;
    },
  },
  pages: authConfig.pages,
  session: {
    strategy: 'jwt',
    maxAge: authConfig.session.maxAge,
  },
  events: {
    async signIn({ user, account, profile }) {
      // Log successful sign-ins
      console.log('User signed in:', user.email);
    },
    async signOut({ token, session }) {
      // Log sign-outs
      console.log('User signed out:', token.email);
    },
  },
}; 