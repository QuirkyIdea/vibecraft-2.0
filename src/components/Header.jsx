import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useWorkflow } from '../context/WorkflowContext';
import LoginButton from './LoginButton';

const Header = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const { user } = useAuth();
    const { currentView, navigateTo } = useWorkflow();

    return (
        <header
            className={`fixed top-0 w-full z-50 transition-all duration-300 ${isScrolled ? 'bg-white/80 backdrop-blur-md shadow-sm' : 'bg-transparent'}`}
        >
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                {/* Logo */}
                <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigateTo('HOME')}>
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-400 flex items-center justify-center text-white font-bold text-lg">
                        I
                    </div>
                    <span className="text-xl font-bold tracking-tight text-gray-900">INVENTIX <span className="text-blue-500">AI</span></span>
                </div>

                {/* Navigation */}
                <nav className="hidden md:flex items-center gap-1 p-1 bg-gray-100/50 rounded-full border border-gray-200 backdrop-blur-sm">
                    {['HOME', 'DASHBOARD', 'PLATFORM'].map((item) => (
                        <button
                            key={item}
                            onClick={() => navigateTo(item)}
                            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${currentView === item
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            {item === 'HOME' ? 'Home' : item === 'DASHBOARD' ? 'My Dashboard' : 'Platform'}
                        </button>
                    ))}
                </nav>

                {/* Auth */}
                <div className="flex items-center gap-4">
                    <LoginButton />
                </div>
            </div>
        </header>
    );
};

export default Header;
