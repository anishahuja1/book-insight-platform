'use client';
import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function QAInterface() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [historyFetched, setHistoryFetched] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const u = new URLSearchParams(window.location.search);
    const q = u.get('q');
    if (q) {
      setInput(q);
    }
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const hist = await api.qa.history();
        if (hist && hist.length > 0) {
          const formatted = [];
          for (let h of hist.reverse()) {
            formatted.push({ role: 'user', content: h.question });
            formatted.push({ role: 'assistant', content: h.answer, sources: h.sources });
          }
          setMessages(formatted);
          if (hist.length > 0) {
            setSessionId(hist[hist.length-1].session_id);
          }
        }
      } catch(e) {
        console.error(e);
      } finally {
        setHistoryFetched(true);
      }
    };
    fetchHistory();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e?: any) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const q = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const res = await api.qa.ask(q, sessionId);
      if (res.session_id) setSessionId(res.session_id);
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: res.answer,
        sources: res.sources
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I encountered an error processing your question.",
        isError: true 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setSessionId('');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] glass-card overflow-hidden shadow-2xl">
      <div className="flex justify-between items-center p-6 border-b border-white/10 bg-black/40 backdrop-blur-md">
        <div>
          <h2 className="font-serif text-3xl font-bold text-primary mb-1">Library AI Assistant</h2>
          <p className="text-xs text-textMuted uppercase tracking-widest">Ask questions about the collected books</p>
        </div>
        <button onClick={handleClear} className="text-xs font-bold uppercase tracking-wider bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg transition-colors border border-white/10 text-white">
          Clear Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-8 bg-gradient-to-b from-transparent to-black/20">
        {messages.length === 0 && historyFetched && (
          <div className="flex-1 flex flex-col items-center justify-center text-center max-w-2xl mx-auto px-4">
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-6 border border-primary/20 shadow-[0_0_50px_rgba(245,158,11,0.1)]">
              <span className="text-4xl filter hue-rotate-15">✨</span>
            </div>
            <h3 className="font-serif text-4xl mb-4 text-textMain leading-tight">How can I assist your literary journey?</h3>
            <p className="text-textMuted mb-10 text-lg">Ask me anything about the books in our database. I can recommend books, summarize topics, or answer specific questions based on the library content.</p>
            
            <div className="flex flex-wrap justify-center gap-3">
              {[
                "What are the best mystery books?", 
                "Recommend books similar to classic literature", 
                "Which books have the highest ratings?"
              ].map(q => (
                <button 
                  key={q} 
                  onClick={() => setInput(q)}
                  className="bg-white/5 hover:bg-primary/20 hover:border-primary/50 border border-white/10 text-sm px-6 py-3 rounded-full transition-all text-textMain text-left shadow-lg"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col w-full max-w-4xl animate-in fade-in slide-in-from-bottom-2 ${m.role === 'user' ? 'self-end items-end' : 'self-start items-start'}`}>
            <span className={`text-[10px] uppercase tracking-widest font-bold mb-2 px-1 ${m.role === 'user' ? 'text-primary' : 'text-textMuted'}`}>
              {m.role === 'user' ? 'You' : 'AI Assistant'}
            </span>
            <div className={`p-5 rounded-2xl shadow-xl ${m.role === 'user' ? 'bg-primary/20 text-white border border-primary/30 rounded-tr-sm' : m.isError ? 'bg-red-500/20 text-red-200 border border-red-500/30' : 'bg-white/5 backdrop-blur-sm text-textMain border border-white/10 rounded-tl-sm'}`}>
              <div className="whitespace-pre-wrap leading-relaxed text-lg">{m.content}</div>
            </div>
            
            {m.role === 'assistant' && m.sources && m.sources.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2 pl-2">
                <span className="text-[10px] uppercase tracking-widest text-textMuted flex items-center mr-1 font-bold">Sources Cited:</span>
                {m.sources.map((s: any, idx: number) => (
                  <Link href={`/books/${s.book_id}`} key={idx} className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-md text-primary transition-colors flex items-center gap-2 font-medium">
                    {s.title}
                    <span className="text-primary/50 bg-black/40 px-1 rounded">{(s.relevance_score * 100).toFixed(0)}%</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="self-start items-start flex flex-col">
            <span className="text-[10px] uppercase tracking-widest font-bold mb-2 px-1 text-textMuted">AI Assistant</span>
            <div className="bg-white/5 border border-white/10 p-5 rounded-2xl rounded-tl-sm flex items-center gap-2 shadow-xl backdrop-blur-sm h-14">
              <div className="w-2.5 h-2.5 rounded-full bg-primary animate-bounce"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-primary animate-bounce" style={{animationDelay: '0.2s'}}></div>
              <div className="w-2.5 h-2.5 rounded-full bg-primary animate-bounce" style={{animationDelay: '0.4s'}}></div>
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-4" />
      </div>

      <div className="p-4 bg-black/40 border-t border-white/10 backdrop-blur-xl">
        <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto relative group">
          <textarea 
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if(e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            disabled={loading}
            placeholder="Ask a question about books... (Press Enter to send)" 
            className="flex-1 bg-white/5 border border-white/10 rounded-2xl pl-6 pr-16 py-4 focus:border-primary focus:bg-white/10 focus:outline-none transition-all text-textMain disabled:opacity-50 resize-none shadow-inner"
            style={{ minHeight: '60px', maxHeight: '150px' }}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="absolute right-2 top-2 bottom-2 aspect-square bg-primary text-background rounded-xl flex items-center justify-center font-bold text-xl hover:bg-primary/90 transition-all disabled:opacity-50 disabled:bg-primary/20 disabled:text-textMuted shadow-lg disabled:shadow-none"
          >
            ↑
          </button>
        </form>
      </div>
    </div>
  );
}
