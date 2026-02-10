import React, { useEffect } from 'react';
import { Star, RotateCcw } from 'lucide-react';
import confetti from 'canvas-confetti';
import { motion } from 'framer-motion';

function ResultsView({ score, totalQuestions, missedCount, onReset, onReview }) {
    const correctCount = totalQuestions - missedCount;

    useEffect(() => {
        if (score >= 70) {
            const duration = 3 * 1000;
            const animationEnd = Date.now() + duration;
            const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

            const random = (min, max) => Math.random() * (max - min) + min;

            const interval = setInterval(function () {
                const timeLeft = animationEnd - Date.now();

                if (timeLeft <= 0) {
                    return clearInterval(interval);
                }

                const particleCount = 50 * (timeLeft / duration);
                confetti(Object.assign({}, defaults, { particleCount, origin: { x: random(0.1, 0.3), y: random(0.2, 0) } }));
                confetti(Object.assign({}, defaults, { particleCount, origin: { x: random(0.7, 0.9), y: random(0.2, 0) } }));
            }, 250);
        }
    }, [score]);

    const passed = score >= 70;

    return (
        <div className="text-center py-12 space-y-10 max-w-2xl mx-auto">
            <motion.div
                initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200, damping: 15 }}
                className={`inline-flex p-8 rounded-3xl ${passed ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'} mb-6 shadow-inner`}
            >
                <Star size={84} fill="currentColor" className="drop-shadow-sm" />
            </motion.div>

            <div className="space-y-4">
                <h2 className="text-5xl font-extrabold text-slate-900 tracking-tight">
                    {passed ? "Journey Complete!" : "Knowledge Gap Detected"}
                </h2>
                <p className="text-slate-500 text-xl">
                    {passed ? "You have successfully mastered this checkpoint." : "A bit more practice is needed to master this topic."}
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div whileHover={{ y: -5 }} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-lg">
                    <div className="text-xs text-slate-500 uppercase tracking-widest font-bold mb-2">Final Score</div>
                    <div className={`text-4xl font-bold ${passed ? 'text-indigo-600' : 'text-amber-600'}`}>
                        {typeof score === 'number' ? Math.round(score) : '0'}%
                    </div>
                </motion.div>

                <motion.div whileHover={{ y: -5 }} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-lg">
                    <div className="text-xs text-slate-500 uppercase tracking-widest font-bold mb-2">Accuracy</div>
                    <div className="text-2xl font-bold text-slate-700">
                        <span className="text-emerald-500">{correctCount}</span>
                        <span className="mx-1 text-slate-300">/</span>
                        <span className="text-slate-900">{totalQuestions}</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 font-medium">Correct Questions</p>
                </motion.div>

                <motion.div whileHover={{ y: -5 }} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-lg">
                    <div className="text-xs text-slate-500 uppercase tracking-widest font-bold mb-2">Mistakes</div>
                    <div className="text-2xl font-bold text-rose-500">
                        {missedCount}
                    </div>
                    <p className="text-xs text-slate-400 mt-1 font-medium">Incorrect Questions</p>
                </motion.div>
            </div>

            <div className="pt-10 flex flex-wrap items-center justify-center gap-4">
                {missedCount > 0 && (
                    <button onClick={onReview} className="btn-primary px-10">
                        Review Missed Concepts
                    </button>
                )}
                <button onClick={onReset} className="btn-outline">
                    <RotateCcw size={20} />
                    Start New Path
                </button>
            </div>
        </div>
    );
}

export default ResultsView;
