import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import SinglePredict from './components/SinglePredict';
import BatchPredict from './components/BatchPredict';
import GeminiAssistant from './components/GeminiAssistant';
import Education from './components/Education';
import ModelInfo from './components/ModelInfo';
import Footer from './components/Footer';
import { checkHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('single');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [activeJobContext, setActiveJobContext] = useState(null);

  const handleConsultWithGemini = (context) => {
    setActiveJobContext(context);
    setActiveTab('assistant');
  };

  useEffect(() => {
    let isMounted = true;
    const verifyBackend = async () => {
      try {
        const res = await checkHealth();
        if (isMounted) {
          if (res.status === 'ok') {
            setBackendStatus('online');
          } else {
            setBackendStatus('offline');
          }
        }
      } catch (err) {
        if (isMounted) {
          setBackendStatus('offline');
        }
      }
    };

    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col text-slate-900">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
      />

      {activeTab === 'single' && (
        <Hero onStartCheck={() => {
          const el = document.getElementById('main-content');
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }} />
      )}

      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'single' && (
          <SinglePredict 
            onNavigateToEdu={() => setActiveTab('education')} 
            onConsultWithGemini={handleConsultWithGemini}
          />
        )}
        {activeTab === 'batch' && <BatchPredict />}
        {activeTab === 'assistant' && (
          <GeminiAssistant 
            jobContext={activeJobContext} 
            onClearJobContext={() => setActiveJobContext(null)} 
          />
        )}
        {activeTab === 'education' && <Education />}
        {activeTab === 'model' && <ModelInfo />}
      </main>

      <Footer setActiveTab={setActiveTab} />
    </div>
  );
}
