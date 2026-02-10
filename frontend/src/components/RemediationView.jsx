import React, { useState, useEffect } from 'react';
import { getRemediation } from '../api';
import { ArrowLeft, Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';

function RemediationView({ missedIndices, onComplete }) {
    const [remediations, setRemediations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRemediation = async () => {
            try {
                const data = await getRemediation();
                setRemediations(data.remediation);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchRemediation();
    }, [missedIndices]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="w-12 h-12 border-4 border-amber-200 border-t-amber-500 rounded-full animate-spin"></div>
            <p className="text-amber-800 font-medium">Consulting Feynman Archives...</p>
        </div>
    );

    return (
        <div className="space-y-8 max-w-3xl mx-auto">
            <div className="bg-amber-50 border border-amber-100 p-8 rounded-2xl text-center">
                <h2 className="text-2xl font-bold text-amber-900 mb-2 font-outfit">Review Needed</h2>
                <p className="text-amber-700/80 text-lg">You missed {missedIndices.length} concepts. Let's simplify them.</p>
            </div>

            <div className="space-y-8">
                {remediations.map((item, i) => {
                    const originalQuestionNumber = missedIndices[i] + 1;
                    return (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.1 }}
                            className="card bg-white border-l-[6px] border-l-amber-400 overflow-hidden"
                        >
                            <div className="flex items-start gap-4 mb-4">
                                <div className="bg-amber-100 p-2 rounded-lg text-amber-600 mt-1">
                                    <Lightbulb size={24} />
                                </div>
                                <div>
                                    <span className="text-xs font-bold text-amber-500 uppercase tracking-wider">
                                        Question #{originalQuestionNumber} • Concept Review
                                    </span>
                                    <h3 className="font-bold text-slate-800 text-lg">{item.question}</h3>
                                </div>
                            </div>

                            <div className="bg-slate-50 p-6 rounded-xl text-slate-700 italic border border-slate-100/50 mb-4 leading-relaxed relative">
                                <span className="absolute top-2 left-3 text-4xl text-slate-200 font-serif opacity-50">"</span>
                                {item.explanation}
                                <span className="absolute bottom-[-10px] right-4 text-4xl text-slate-200 font-serif opacity-50">"</span>
                            </div>

                            <div className="flex items-center gap-2 text-sm text-emerald-600 font-medium bg-emerald-50 px-4 py-3 rounded-lg w-fit">
                                <span className="font-bold bg-white px-1.5 rounded text-emerald-700 border border-emerald-100">✓</span> Correct Answer: {item.correct_answer}
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            <button onClick={onComplete} className="w-full btn-outline justify-center py-4 text-slate-600 hover:text-indigo-600 border-slate-200 hover:border-indigo-200">
                <ArrowLeft size={18} />
                Return to Study Material & Retake
            </button>
        </div>
    );
}

export default RemediationView;
