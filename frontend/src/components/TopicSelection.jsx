import React, { useState } from 'react';
import { Layers, Cpu, BrainCircuit, Code, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const TOPICS = [
    {
        id: 'Python',
        label: 'Python Data Science',
        icon: Code,
        desc: 'Master the world\'s most popular language for Data Science.',
        objectives: ["Python Data Structures", "Functions and Modules", "Object-Oriented Programming"],
        color: "from-blue-500 to-cyan-400"
    },
    {
        id: 'AI',
        label: 'Artificial Intelligence',
        icon: Cpu,
        desc: 'Uncover the foundations of Artificial Intelligence and Search.',
        objectives: ["AI Foundations", "Search Algorithms", "Logic & Reasoning"],
        color: "from-purple-500 to-indigo-400"
    },
    {
        id: 'ML',
        label: 'Machine Learning',
        icon: BrainCircuit,
        desc: 'Build predictive models with Machine Learning techniques.',
        objectives: ["Supervised Learning", "Linear Regression", "Decision Trees"],
        color: "from-emerald-500 to-teal-400"
    },
    {
        id: 'DL',
        label: 'Deep Learning',
        icon: Layers,
        desc: 'Deep dive into Neural Networks and Computer Vision.',
        objectives: ["Neural Architectures", "Backpropagation", "CNNs & Vision"],
        color: "from-orange-500 to-amber-400"
    }
];

function TopicSelection({ onStart }) {
    const [selected, setSelected] = useState(TOPICS[0]);

    return (
        <div className="space-y-10">
            <div className="text-center space-y-4">
                <h2 className="text-4xl font-bold text-slate-900 font-outfit tracking-tight">
                    Choose Your Path
                </h2>
                <p className="text-slate-500 text-lg max-w-2xl mx-auto">
                    Select a domain to generate a personalized learning curriculum powered by AI.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {TOPICS.map((topic) => {
                    const Icon = topic.icon;
                    const isSelected = selected.id === topic.id;
                    return (
                        <motion.div
                            key={topic.id}
                            onClick={() => setSelected(topic)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`cursor-pointer p-6 rounded-2xl border-2 transition-all relative overflow-hidden group ${isSelected
                                    ? 'border-indigo-600 bg-white shadow-xl shadow-indigo-100'
                                    : 'border-white bg-white/60 hover:border-indigo-200'
                                }`}
                        >
                            <div className={`absolute top-0 right-0 p-32 opacity-5 rounded-full blur-3xl bg-gradient-to-br ${topic.color} translate-x-10 -translate-y-10 group-hover:opacity-10 transition-opacity`}></div>

                            <div className="flex items-start gap-4 relative z-10">
                                <div className={`p-4 rounded-xl shadow-sm ${isSelected ? `bg-gradient-to-br ${topic.color} text-white` : 'bg-slate-100 text-slate-500'}`}>
                                    <Icon size={28} />
                                </div>
                                <div>
                                    <h3 className={`font-bold text-xl mb-1 ${isSelected ? 'text-slate-900' : 'text-slate-700'}`}>
                                        {topic.label}
                                    </h3>
                                    <p className="text-sm text-slate-500 leading-relaxed opacity-90">{topic.desc}</p>
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/50 shadow-sm"
            >
                <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex-1">
                        <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                            Curriculum Objectives
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {selected.objectives.map((obj, i) => (
                                <span key={i} className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium border border-indigo-100">
                                    {obj}
                                </span>
                            ))}
                        </div>
                    </div>

                    <button
                        onClick={() => onStart(selected.label, selected.objectives)}
                        className="w-full md:w-auto btn-primary whitespace-nowrap group text-lg"
                    >
                        <span>Start {selected.id} Journey</span>
                        <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </motion.div>
        </div>
    );
}

export default TopicSelection;
