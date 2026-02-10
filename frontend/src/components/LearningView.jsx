import React from 'react';
import { PlayCircle, Award, Target, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css'; // Markdown code block styling

function LearningView({ topic, summary, relevanceScore, onNext }) {
    // If relevanceScore is not passed, default to 0. 
    // App.jsx needs to be updated to pass this prop.
    const score = relevanceScore || 0;

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between border-b border-slate-200/60 pb-6 gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900 mb-2 font-outfit">Module: {topic}</h2>
                    <p className="text-slate-500 text-lg">Master these concepts to achieve your learning goals.</p>
                </div>

                <div className="flex items-center gap-4">
                    {/* Relevance Score Badge */}
                    <div className={`flex flex-col items-end px-4 py-2 rounded-xl border ${score >= 80 ? 'bg-emerald-50 border-emerald-100' : 'bg-amber-50 border-amber-100'
                        }`}>
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-1 opacity-70">
                            <Target size={14} />
                            Relevance Score
                        </div>
                        <div className={`text-2xl font-bold ${score >= 80 ? 'text-emerald-600' : 'text-amber-600'
                            }`}>
                            {score.toFixed(0)}%
                        </div>
                    </div>

                    <div className="hidden md:flex bg-indigo-50 text-indigo-700 px-4 py-2 rounded-full text-sm font-semibold items-center gap-2 border border-indigo-100 shadow-sm">
                        <Award size={16} />
                        Content Ready
                    </div>
                </div>
            </div>

            {/* Main Content Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 md:p-10 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 to-purple-500"></div>

                <div className="prose prose-lg prose-indigo max-w-none text-slate-700 font-inter">
                    <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                        {summary || "No summary available."}
                    </ReactMarkdown>
                </div>
            </div>

            {/* Study Tip */}
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 rounded-xl p-6 flex items-start gap-4">
                <div className="bg-white p-2 rounded-lg shadow-sm text-indigo-600 mt-1">
                    <BookOpen size={24} />
                </div>
                <div>
                    <h4 className="font-bold text-indigo-900 text-sm uppercase tracking-wide mb-1">Study Tip</h4>
                    <p className="text-indigo-800/80 text-sm leading-relaxed">
                        Read the material above carefully. The AI has tailored this content specifically to your learning goals.
                        The upcoming quiz will verify your mastery of these concepts.
                    </p>
                </div>
            </div>

            <div className="flex justify-end pt-4">
                <button onClick={onNext} className="btn-primary text-lg shadow-xl shadow-indigo-500/20 hover:shadow-indigo-500/30">
                    <span>Begin Assessment</span>
                    <PlayCircle size={24} />
                </button>
            </div>
        </div>
    );
}

export default LearningView;
