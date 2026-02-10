import React, { useState, useEffect } from 'react';
import { getQuiz } from '../api';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle } from 'lucide-react';

function QuizView({ onSubmit }) {
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                const data = await getQuiz();
                setQuestions(data.questions);
                const initialAnswers = {};
                data.questions.forEach((q, i) => initialAnswers[i] = null);
                setAnswers(initialAnswers);
            } catch (e) {
                console.error("Failed to fetch quiz", e);
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, []);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const handleSelect = (qIndex, optionIndex) => {
        setAnswers(prev => ({
            ...prev,
            [qIndex]: optionIndex
        }));
    };

    const handleSubmit = () => {
        console.log("Submitting answers:", answers);
        const answerArray = questions.map((_, i) => answers[i]);
        if (answerArray.some(a => a === null)) {
            alert("Please answer all questions before submitting.");
            return;
        }
        onSubmit(answerArray);
    };

    const answeredCount = Object.values(answers).filter(a => a !== null).length;
    const progress = questions.length > 0 ? (answeredCount / questions.length) * 100 : 0;

    if (loading) return (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-500 rounded-full animate-spin"></div>
            <p className="text-indigo-800 font-medium font-outfit">Preparing your assessment...</p>
        </div>
    );

    return (
        <div className="space-y-8 max-w-3xl mx-auto">
            <div className="sticky top-0 bg-white/95 backdrop-blur-md py-4 z-10 border-b border-slate-100 -mx-4 px-4 md:mx-0 md:px-0">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-2xl font-bold text-slate-900 font-outfit">Knowledge Check</h2>
                    <span className="text-sm font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
                        {answeredCount} / {questions.length} Answered
                    </span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-indigo-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                    />
                </div>
            </div>

            <div className="space-y-8 pb-10">
                {questions.map((q, index) => (
                    <motion.div
                        key={q.id || index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="card bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow"
                    >
                        <h3 className="text-lg font-bold text-slate-800 mb-6 flex gap-4">
                            <span className="bg-indigo-600 text-white w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold shrink-0 self-start mt-0.5 shadow-md shadow-indigo-200">
                                {index + 1}
                            </span>
                            <span className="leading-relaxed pt-0.5">{q.question}</span>
                        </h3>

                        <div className="space-y-3 pl-0 md:pl-12">
                            {q.options.map((opt, optIndex) => {
                                const label = String.fromCharCode(65 + optIndex); // A, B, C, D
                                const isSelected = answers[index] === optIndex;

                                return (
                                    <label
                                        key={optIndex}
                                        className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all relative overflow-hidden group ${isSelected
                                            ? 'border-indigo-500 bg-indigo-50 shadow-inner'
                                            : 'border-slate-100 hover:border-indigo-200 hover:bg-slate-50'
                                            }`}
                                    >
                                        <input
                                            type="radio"
                                            name={`question-${index}`}
                                            checked={isSelected}
                                            onChange={() => handleSelect(index, optIndex)}
                                            className="sr-only"
                                        />

                                        {/* Standard Radio Circle */}
                                        <div className={`w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center transition-all shrink-0 ${isSelected
                                            ? 'border-indigo-600 bg-white'
                                            : 'border-slate-300 group-hover:border-indigo-400'
                                            }`}>
                                            {isSelected && <div className="w-3 h-3 bg-indigo-600 rounded-full" />}
                                        </div>

                                        {/* A/B/C/D Badge */}
                                        <div className={`w-7 h-7 rounded-md border flex items-center justify-center text-xs font-bold transition-colors shrink-0 mr-4 ${isSelected
                                            ? 'bg-indigo-100 text-indigo-700 border-indigo-200'
                                            : 'bg-slate-50 text-slate-500 border-slate-200'
                                            }`}>
                                            {label}
                                        </div>

                                        <span className={`text-base font-medium leading-normal ${isSelected ? 'text-indigo-900' : 'text-slate-700'}`}>
                                            {opt}
                                        </span>
                                    </label>
                                );
                            })}
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="pt-6 pb-12">
                <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={answeredCount < questions.length}
                    className="w-full btn-primary"
                >
                    {answeredCount < questions.length ? 'Answer All Questions to Continue' : 'Submit Assessment'}
                    {answeredCount === questions.length && <CheckCircle2 size={24} />}
                </button>
            </div>
        </div>
    );
}

export default QuizView;
