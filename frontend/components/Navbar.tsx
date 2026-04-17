"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { User, LogOut } from "lucide-react";
import { LiveStatus } from "./LiveStatus";

export function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  useEffect(() => {
    if (token) {
      localStorage.setItem("auth_token", token);
      setIsLoggedIn(true);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      const storedToken = localStorage.getItem("auth_token");
      if (storedToken) {
        setIsLoggedIn(true);
      }
    }
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    setIsLoggedIn(false);
    window.location.href = "/login";
  };

  return (
    <header className="bg-white border-b sticky top-0 z-10 px-6 py-4 flex justify-between items-center shadow-sm backdrop-blur-md bg-white/90">
      <Link href="/dashboard" className="flex items-center gap-2 group transition-transform active:scale-95">
        <div className="w-10 h-10 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-100 group-hover:shadow-blue-200 transition-all">
          P
        </div>
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
          AsyncDoc
        </h1>
      </Link>

      <div className="flex items-center gap-6">
        <LiveStatus />
        
        {isLoggedIn ? (
          <div className="flex items-center gap-4">
            <div className="h-8 w-px bg-gray-200" />
            <button className="flex items-center gap-2 p-1 px-3 rounded-full bg-gray-50 border border-gray-100 hover:bg-white hover:shadow-sm transition-all">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                <User size={14} />
              </div>
              <span className="text-sm font-medium text-gray-700">Account</span>
            </button>
            <button 
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <Link 
            href="/login"
            className="px-5 py-2 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-100 hover:shadow-blue-200 transition-all active:scale-95"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
}
