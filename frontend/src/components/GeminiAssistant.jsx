import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  Sparkles, 
  Trash2, 
  Briefcase,
  X,
  Zap
} from 'lucide-react';
import { chatWithAssistant } from '../api';

const QUICK_PROMPTS = [
  '✈️ Saya disuruh beli tiket pesawat travel rekanan untuk interview, apakah penipuan?',
  '💳 Diminta bayar Rp 350.000 untuk biaya modul psikotes dan seragam kerja.',
  '📱 Ditawari freelance like video YouTube & deposit tugas Telegram, aman tidak?',
  '🪪 HRD meminta foto selfie dengan KTP dan buku tabungan sebelum interview.',
  '🔍 Bagaimana cara membedakan email rekruter asli vs penipuan?',
];

export default function GeminiAssistant({ jobContext, onClearJobContext }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 
        'Halo! Saya **JobShield Security Advisor** didukung oleh **Google Gemini AI**. 🛡️✨\n\n' +
        'Saya siap membantu Anda memverifikasi pesan mencurigakan, memeriksa keabsahan surat panggilan tes, menganalisis modus penipuan, atau memberikan panduan perlindungan data pribadi.\n\n' +
        'Silakan ketik pertanyaan Anda atau pilih salah satu pertanyaan cepat di bawah!',
      isLiveGemini: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInput('');
    setLoading(true);

    try {
      // Siapkan payload messages (hanya role & content untuk backend)
      const apiMessages = newHistory.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await chatWithAssistant(apiMessages, jobContext);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          model: res.model,
          isLiveGemini: res.is_live_gemini,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Terjadi kendala: ${err.message || 'Gagal menghubungi asisten'}. Silakan coba kembali.`,
          isLiveGemini: false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Percakapan telah direset. Silakan ajukan pertanyaan seputar keamanan lowongan kerja!',
        isLiveGemini: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="space-y-4 max-w-5xl mx-auto">
      {/* Assistant Header Card */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900">Asisten AI Gemini</h2>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Gemini 2.5 Flash Aktif</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Konsultan keamanan karir interaktif untuk evaluasi tawaran kerja dan modus penipuan.
            </p>
          </div>
        </div>

        {/* Clear Conversation Action */}
        <div className="flex items-center space-x-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={handleClearChat}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer"
            title="Bersihkan Percakapan"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Active Job Context Pill (if forwarded from Single Predict) */}
      {jobContext && (
        <div className="bg-blue-50/90 border border-blue-200 rounded-xl px-4 py-2.5 flex items-center justify-between text-xs text-blue-900 shadow-sm animate-fade-in">
          <div className="flex items-center space-x-2 overflow-hidden">
            <Briefcase className="w-4 h-4 text-blue-600 shrink-0" />
            <span className="font-semibold">Konteks Aktif:</span>
            <span className="truncate max-w-xs sm:max-w-md font-medium text-blue-800">
              "{jobContext.title}" — {jobContext.prediksi} ({jobContext.probabilitas_palsu})
            </span>
          </div>
          {onClearJobContext && (
            <button
              onClick={onClearJobContext}
              className="p-1 hover:bg-blue-100 rounded-lg text-blue-700 transition-colors ml-2 cursor-pointer"
              title="Hapus konteks lowongan ini"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Chat Window Container */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm flex flex-col h-[560px] overflow-hidden">
        {/* Messages List Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                className={`flex items-start space-x-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shrink-0 text-xs shadow-sm mt-0.5">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-500/20'
                      : 'bg-slate-50 text-slate-800 border border-slate-200/80 rounded-tl-none'
                  }`}
                >
                  {/* Message Content with simple markdown rendering */}
                  <div className="whitespace-pre-line space-y-1">
                    {msg.content}
                  </div>

                  {/* Metadata footer */}
                  <div
                    className={`mt-2 pt-1.5 flex items-center justify-between text-[10px] border-t ${
                      isUser
                        ? 'border-blue-500/50 text-blue-200'
                        : 'border-slate-200 text-slate-400'
                    }`}
                  >
                    <span>
                      {!isUser && (
                        msg.isLiveGemini 
                          ? '✨ Google Gemini 2.5 Flash' 
                          : '🛡️ JobShield Knowledge Base'
                      )}
                    </span>
                    <span>{msg.timestamp}</span>
                  </div>
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 text-white flex items-center justify-center shrink-0 text-xs shadow-sm mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex items-start space-x-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-none p-3.5 text-xs text-slate-500 flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
                <span>Asisten Gemini sedang menganalisis pertanyaan Anda...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="p-3 bg-slate-50/80 border-t border-slate-100 overflow-x-auto scrollbar-none flex items-center space-x-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider shrink-0 mr-1">
            Saran:
          </span>
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSendMessage(prompt)}
              className="px-3 py-1.5 rounded-lg text-xs bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200/80 whitespace-nowrap transition-colors cursor-pointer shrink-0 shadow-2xs"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Bar Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="p-3 sm:p-4 bg-white border-t border-slate-200 flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanyakan ke Asisten Gemini (contoh: 'Apakah aman jika saya diminta transfer dana tes?')..."
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-xs sm:text-sm bg-slate-50/50 focus:bg-white"
          />

          <button
            type="submit"
            disabled={!input.trim() || loading}
            className={`p-2.5 rounded-xl text-white transition-all flex items-center justify-center cursor-pointer ${
              !input.trim() || loading
                ? 'bg-slate-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-500/25'
            }`}
            title="Kirim Pesan"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
