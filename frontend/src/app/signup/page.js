"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { registerUser } from '@/utils/api';
import toast, { Toaster } from 'react-hot-toast';
import { Mail, Lock, User, ArrowRight, Sparkles, Eye, EyeOff, Hash, BookOpen } from 'lucide-react';
import Link from 'next/link';

export default function Signup() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '', // This will be the email
    password: '',
    full_name: '',
    roll_number: '',
    branch: 'AIML' // Default
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await registerUser(formData);
      toast.success('Account Created! Redirecting...');
      setTimeout(() => router.push('/login'), 1500);
    } catch (error) {
      console.error("Signup Error Details:", error.response?.data); // Check console for exact details
      
      let errorMessage = "Signup Failed. Try again.";

      // 1. Handle "422 Validation Error" (The Array of Objects)
      if (error.response?.data?.detail && Array.isArray(error.response.data.detail)) {
        // Grab the first error message from the list (e.g., "field required")
        const firstError = error.response.data.detail[0];
        errorMessage = `${firstError.loc[1]}: ${firstError.msg}`;
      } 
      // 2. Handle standard String errors (e.g., "Email already exists")
      else if (typeof error.response?.data?.detail === "string") {
        errorMessage = error.response.data.detail;
      }

      toast.error(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <Toaster toastOptions={{ style: { background: '#1e293b', color: '#fff' } }}/>
      
      {/* Background Glows */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-500 shadow-2xl shadow-purple-500/50 mb-4">
            <Sparkles className="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Join the Club
          </h1>
          <p className="text-slate-400 text-sm">Create your student profile</p>
        </div>

        {/* Form Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
          <form onSubmit={handleSignup} className="space-y-4">
            
            {/* Full Name */}
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Full Name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                <input 
                  name="full_name"
                  type="text" 
                  className="w-full bg-white/5 border border-white/10 text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/20 transition-all placeholder-slate-600 text-sm"
                  placeholder="Goutham Eppili"
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">College Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                <input 
                  name="username"
                  type="email" 
                  className="w-full bg-white/5 border border-white/10 text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/20 transition-all placeholder-slate-600 text-sm"
                  placeholder="student@vishnu.edu.in"
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Roll Number & Branch (Side by Side) */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Roll No</label>
                <div className="relative">
                  <Hash className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                  <input 
                    name="roll_number"
                    type="text" 
                    className="w-full bg-white/5 border border-white/10 text-white pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:border-purple-400 text-sm"
                    placeholder="23PA1A..."
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Branch</label>
                <div className="relative">
                  <BookOpen className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                  <select 
                    name="branch"
                    className="w-full bg-white/5 border border-white/10 text-slate-300 pl-10 pr-4 py-3 rounded-xl focus:outline-none focus:border-purple-400 text-sm appearance-none"
                    onChange={handleChange}
                  >
                    <option value="AIML" className="bg-slate-900">AIML</option>
                    <option value="CSE" className="bg-slate-900">CSE</option>
                    <option value="IT" className="bg-slate-900">IT</option>
                    <option value="ECE" className="bg-slate-900">ECE</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
                <input 
                  name="password"
                  type={showPassword ? "text" : "password"} 
                  className="w-full bg-white/5 border border-white/10 text-white pl-10 pr-10 py-3 rounded-xl focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/20 transition-all placeholder-slate-600 text-sm"
                  placeholder="••••••••"
                  onChange={handleChange}
                  required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
                  {showPassword ? <EyeOff size={16}/> : <Eye size={16}/>}
                </button>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold py-3 rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all mt-4 flex items-center justify-center gap-2 group"
            >
              {loading ? "Creating Profile..." : <>Create Account <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform"/></>}
            </button>
          </form>

          <p className="text-center text-sm text-slate-400 mt-6">
            Already have an account? <Link href="/login" className="text-purple-400 hover:text-purple-300 font-medium">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}