import React, { useState, useEffect } from 'react';
import { History, Calendar, TrendingUp, Award } from 'lucide-react';
import { getHistory } from '../api';
import { motion } from 'framer-motion';

const HistoryView = ({ onClose }) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            setLoading(true);
            const data = await getHistory();
            setHistory(data);
        } catch (err) {
            setError('Failed to load history');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getScoreColor = (score) => {
        if (score >= 70) return 'text-emerald-600 bg-emerald-50';
        if (score >= 50) return 'text-amber-600 bg-amber-50';
        return 'text-rose-600 bg-rose-50';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="relative w-12 h-12">
                    <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-6 rounded-xl border border-red-100">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-slate-800 flex items-center gap-3 font-outfit">
                        <History className="w-8 h-8 text-indigo-600" />
                        Learning History
                    </h2>
                    <p className="text-slate-500 mt-2">Track your progress and review past sessions</p>
                </div>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-slate-600 hover:text-slate-800 transition-colors"
                    >
                        Close
                    </button>
                )}
            </div>

            {history.length === 0 ? (
                <div className="text-center py-20">
                    <History className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-600 mb-2">No History Yet</h3>
                    <p className="text-slate-400">Complete your first learning journey to see it here!</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {history.map((session, index) => (
                        <motion.div
                            key={session.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="bg-white rounded-2xl p-6 border border-slate-200/50 hover:shadow-lg transition-all duration-200 hover:border-indigo-200"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <h3 className="text-xl font-semibold text-slate-800 mb-2">
                                        {session.topic}
                                    </h3>
                                    <div className="flex items-center gap-4 text-sm text-slate-500">
                                        <div className="flex items-center gap-1.5">
                                            <Calendar className="w-4 h-4" />
                                            {formatDate(session.created_at)}
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <TrendingUp className="w-4 h-4" />
                                            Quality: {session.relevance_score?.toFixed(0)}%
                                        </div>
                                    </div>
                                </div>
                                <div className={`px-4 py-2 rounded-xl font-bold text-lg ${getScoreColor(session.score)}`}>
                                    <div className="flex items-center gap-2">
                                        <Award className="w-5 h-5" />
                                        {session.score?.toFixed(0)}%
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default HistoryView;
