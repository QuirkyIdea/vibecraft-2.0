import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

const LoginButton = () => {
    const { user, login, logout } = useAuth();

    return (
        <div className="relative z-50">
            <AnimatePresence mode="wait">
                {user ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="flex items-center gap-4 bg-glass-dark border border-white/10 rounded-full pl-2 pr-4 py-1.5"
                    >
                        {user.picture && (
                            <img
                                src={user.picture}
                                alt={user.name}
                                className="w-8 h-8 rounded-full border border-blue-400"
                            />
                        )}
                        <span className="text-sm font-medium text-white hidden sm:block">
                            {user.given_name || user.name}
                        </span>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={logout}
                            className="bg-red-500/20 hover:bg-red-500/40 text-red-300 text-xs px-3 py-1.5 rounded-full transition-colors border border-red-500/30"
                        >
                            Sign Out
                        </motion.button>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <GoogleLogin
                            onSuccess={login}
                            onError={() => {
                                console.log('Login Failed');
                            }}
                            theme="filled_black"
                            shape="pill"
                            text="signin_with"
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default LoginButton;
