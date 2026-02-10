import React, { useState } from 'react';
import { BookOpen, CheckCircle, Brain, LayoutDashboard } from 'lucide-react';
import { startLearning, getQuiz, submitQuiz, getRemediation, resetState } from './api';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

// Components
import TopicSelection from './components/TopicSelection';
import LearningView from './components/LearningView';
import QuizView from './components/QuizView';
import RemediationView from './components/RemediationView';
import ResultsView from './components/ResultsView';

function App() {
  const [step, setStep] = useState('input'); // input, learning, quiz, remediation, complete
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [state, setState] = useState({
    topic: '',
    summary: '',
    score: 0,
    missedIndices: [],
    remediationData: [],
    relevanceScore: 0,
    totalQuestions: 0
  });

  React.useEffect(() => {
    window.scrollTo(0, 0);
  }, [step]);

  const handleStart = async (topic, objectives) => {
    setLoading(true);
    setError(null);
    try {
      const data = await startLearning(topic, objectives);
      setState(prev => ({ ...prev, topic, summary: data.summary, relevanceScore: data.relevance_score, totalQuestions: 0 }));
      setStep('learning');
    } catch (err) {
      setError('Failed to start learning. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = () => {
    setStep('quiz');
  };

  const handleSubmitQuiz = async (userAnswers) => {
    setLoading(true);
    try {
      const result = await submitQuiz(userAnswers);
      setState(prev => ({
        ...prev,
        score: result.score,
        missedIndices: result.missed_indices,
        totalQuestions: userAnswers.length
      }));

      setStep('complete');
    } catch (err) {
      setError('Failed to submit quiz.');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = () => {
    setStep('remediation');
  };

  const handleFinishRemediation = () => {
    setStep('learning');
  };

  const handleReset = async () => {
    await resetState();
    setStep('input');
    setState({ topic: '', summary: '', score: 0, missedIndices: [], remediationData: [], relevanceScore: 0, totalQuestions: 0 });
  };

  const steps = [
    { id: 'input', label: 'Selection', icon: LayoutDashboard },
    { id: 'learning', label: 'Study', icon: BookOpen },
    { id: 'quiz', label: 'Practice', icon: CheckCircle },
    { id: 'remediation', label: 'Review', icon: Brain },
    { id: 'complete', label: 'Results', icon: CheckCircle },
  ];

  const currentStepIndex = steps.findIndex(s => s.id === step);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  return (
    <div className="min-h-screen flex text-slate-800 font-inter">
      {/* Sidebar */}
      <aside className="w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/50 p-6 flex flex-col fixed h-full z-10 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-pink-500 bg-clip-text text-transparent mb-10 flex items-center gap-2 font-outfit">
          <Brain className="w-8 h-8 text-indigo-600" />
          AutoLearner
        </h1>

        <div className="mb-8">
          <div className="flex justify-between text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-slate-100/50 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-indigo-500 to-pink-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
            />
          </div>
        </div>

        <nav className="space-y-2 flex-1">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            const isActive = s.id === step;
            const isCompleted = idx < currentStepIndex;

            return (
              <div
                key={s.id}
                className={`flex items-center gap-3 p-3.5 rounded-xl transition-all duration-200 ${isActive ? 'bg-indigo-50 text-indigo-700 font-semibold shadow-sm' :
                  isCompleted ? 'text-slate-600' : 'text-slate-400'
                  }`}
              >
                <Icon size={20} className={isActive ? 'text-indigo-600' : ''} />
                <span className="font-medium">{s.label}</span>
                {isCompleted && <CheckCircle size={16} className="ml-auto text-emerald-500" />}
              </div>
            );
          })}
        </nav>

        <button
          onClick={handleReset}
          className="mt-auto flex items-center gap-2 text-slate-400 hover:text-rose-500 transition-colors p-2 text-sm font-medium"
        >
          <span>Restart Journey</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-72 p-12">
        <div className="max-w-5xl mx-auto">
          <AnimatePresence mode='wait'>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 border border-red-100 flex items-center gap-2"
              >
                ⚠️ {error}
              </motion.div>
            )}

            {loading ? (
              <motion.div
                key="loader"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-32"
              >
                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                </div>
                <p className="text-slate-400 mt-6 font-medium tracking-wide">AI AGENT WORKING...</p>
              </motion.div>
            ) : (
              <motion.div
                key={step}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {step === 'input' && <TopicSelection onStart={handleStart} />}
                {step === 'learning' && (
                  <LearningView
                    topic={state.topic}
                    summary={state.summary}
                    relevanceScore={state.relevanceScore}
                    onNext={handleStartQuiz}
                  />
                )}
                {step === 'quiz' && (
                  <QuizView onSubmit={handleSubmitQuiz} />
                )}
                {step === 'remediation' && (
                  <RemediationView
                    missedIndices={state.missedIndices}
                    onComplete={handleFinishRemediation}
                  />
                )}
                {step === 'complete' && (
                  <ResultsView
                    score={state.score}
                    totalQuestions={state.totalQuestions}
                    missedCount={state.missedIndices.length}
                    onReset={handleReset}
                    onReview={handleReview}
                  />
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
