import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import { login, register } from '../api';

const AuthView = ({ onLoginSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (isLogin) {
                const data = await login(formData.username, formData.password);
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('username', formData.username);
                onLoginSuccess();
            } else {
                if (formData.password !== formData.confirmPassword) {
                    setError('Passwords do not match');
                    setLoading(false);
                    return;
                }
                await register(formData.username, formData.email, formData.password);
                // After registration, auto-login
                const data = await login(formData.username, formData.password);
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('username', formData.username);
                onLoginSuccess();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-white rounded-3xl shadow-2xl shadow-indigo-100/50 border border-slate-100 p-8"
            >
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-50 rounded-2xl mb-4">
                        <Brain className="w-8 h-8 text-indigo-600" />
                    </div>
                    <h2 className="text-3xl font-bold text-slate-900 font-outfit">
                        {isLogin ? 'Welcome Back' : 'Create Account'}
                    </h2>
                    <p className="text-slate-500 mt-2 font-medium">
                        {isLogin ? 'Continue your learning journey' : 'Start your autonomous learning experience'}
                    </p>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="mb-6 p-4 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl text-sm font-medium flex items-center gap-2"
                    >
                        <div className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse" />
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-1">
                        <label className="text-sm font-semibold text-slate-700 ml-1">Username</label>
                        <div className="relative">
                            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="text"
                                name="username"
                                required
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="johndoe"
                                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400"
                            />
                        </div>
                    </div>

                    {!isLogin && (
                        <div className="space-y-1">
                            <label className="text-sm font-semibold text-slate-700 ml-1">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="email"
                                    name="email"
                                    required
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="john@example.com"
                                    className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400"
                                />
                            </div>
                        </div>
                    )}

                    <div className="space-y-1">
                        <label className="text-sm font-semibold text-slate-700 ml-1">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="password"
                                name="password"
                                required
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="••••••••"
                                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400"
                            />
                        </div>
                    </div>

                    {!isLogin && (
                        <div className="space-y-1">
                            <label className="text-sm font-semibold text-slate-700 ml-1">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    required
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400"
                                />
                            </div>
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2 group disabled:opacity-70"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                {isLogin ? 'Sign In' : 'Sign Up'}
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 pt-6 border-t border-slate-100 text-center">
                    <p className="text-slate-500 font-medium">
                        {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
                        <button
                            onClick={() => setIsLogin(!isLogin)}
                            className="text-indigo-600 hover:text-indigo-700 font-bold ml-1"
                        >
                            {isLogin ? 'Create Account' : 'Sign In'}
                        </button>
                    </p>
                </div>
            </motion.div>
        </div>
    );
};

export default AuthView;
