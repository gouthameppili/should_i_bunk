import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white p-4">
      <div className="text-center max-w-2xl">
        <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent mb-4">
          Should I Bunk?
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          The AI-powered attendance strategist for B.Tech students.
          Analyze strictness, predict risk, and sleep peacefully.
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full font-semibold transition-all">
              Login
            </button>
          </Link>
          <Link href="/signup">
            <button className="px-8 py-3 border border-gray-600 hover:border-gray-400 rounded-full font-semibold transition-all">
              Register
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}