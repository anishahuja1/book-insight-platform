'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function BookDetail() {
  const { id } = useParams();
  const [book, setBook] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    if(!id) return;
    const fetchBook = async () => {
      try {
        const res = await api.books.detail(id as string);
        setBook(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchBook();
  }, [id]);

  if (loading) return <div className="animate-pulse glass-card h-[60vh] flex items-center justify-center text-textMuted">Loading book details...</div>;
  if (!book) return <div className="text-center py-20 text-textMuted">Book not found.</div>;

  const insight = book.insight || {};
  const recs = book.recommended_books || [];

  return (
    <div className="flex flex-col gap-8">
      <Link href="/" className="text-primary hover:text-white transition-colors w-max text-sm uppercase tracking-widest font-bold">
        ← Back to Library
      </Link>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 glass-card p-4 h-max">
          {book.cover_image_url ? (
            <img src={book.cover_image_url} alt={book.title} className="w-full rounded-lg shadow-xl" />
          ) : (
            <div className="w-full aspect-[2/3] bg-black/40 rounded-lg flex items-center justify-center font-serif text-textMuted">
              No Cover
            </div>
          )}
          <a href={book.book_url} target="_blank" rel="noreferrer" className="block text-center mt-4 text-xs text-textMuted hover:text-primary transition-colors">
            View Original Source ↗
          </a>
        </div>
        
        <div className="md:col-span-2 flex flex-col gap-6">
          <div className="glass-card p-8">
            <div className="flex flex-wrap gap-2 items-center mb-4">
              <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-primary/30">
                {book.genre || 'Uncategorized'}
              </span>
              <span className="bg-white/10 text-textMain px-3 py-1 rounded-full text-xs font-bold border border-white/10">
                ★ {book.rating || 'N/A'} ({book.reviews_count} reviews)
              </span>
              {book.price && (
                <span className="bg-white/10 text-textMain px-3 py-1 rounded-full text-xs font-bold border border-white/10">
                  {book.price}
                </span>
              )}
            </div>
            
            <h1 className="font-serif text-3xl md:text-5xl font-bold mb-2 leading-tight">
              {book.title}
            </h1>
            <p className="text-xl text-textMuted mb-8 font-serif italic">By {book.author}</p>
            
            <h3 className="text-sm uppercase tracking-widest font-bold text-white/50 mb-2">Description</h3>
            <p className="text-textMain/80 leading-relaxed mb-6">
              {book.description || 'No description available for this book.'}
            </p>
            
            <Link href={`/qa?q=Tell me about ${encodeURIComponent(book.title)}`} className="inline-block bg-primary text-background px-6 py-3 rounded-lg font-bold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20">
              Ask AI About This Book
            </Link>
          </div>
          
          <div className="glass-card overflow-hidden">
            <div className="flex flex-wrap border-b border-white/10 bg-black/20">
              {['summary', 'genre', 'sentiment', 'recommendations'].map(tab => (
                <button 
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 min-w-[120px] py-3 text-sm font-bold uppercase tracking-wider transition-colors ${activeTab === tab ? 'text-primary border-b-2 border-primary bg-white/5' : 'text-textMuted hover:text-textMain hover:bg-white/5'}`}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className="p-6 min-h-[250px]">
              {activeTab === 'summary' && (
                <div className="animate-in fade-in slide-in-from-bottom-2">
                  <h3 className="font-serif text-xl font-bold mb-4 text-primary">AI Summary</h3>
                  <p className="text-textMain/90 leading-relaxed text-lg">{insight.summary || <span className="text-textMuted italic">Insight generation pending or not available.</span>}</p>
                </div>
              )}
              {activeTab === 'genre' && (
                <div className="animate-in fade-in slide-in-from-bottom-2">
                  <h3 className="font-serif text-xl font-bold mb-4 text-primary">AI Predicted Genre</h3>
                  <p className="text-textMain/90 text-2xl font-bold">{insight.genre_predicted || <span className="text-textMuted italic text-base">Pending</span>}</p>
                </div>
              )}
              {activeTab === 'sentiment' && (
                <div className="animate-in fade-in slide-in-from-bottom-2">
                  <h3 className="font-serif text-xl font-bold mb-6 text-primary">Sentiment Analysis</h3>
                  <div className="flex flex-col gap-6 w-full max-w-md">
                    <span className="text-3xl font-bold capitalize text-white">{insight.sentiment || 'Pending'}</span>
                    {insight.sentiment_score !== undefined && (
                      <div className="flex flex-col gap-2">
                        <div className="flex justify-between text-xs text-textMuted font-bold uppercase tracking-widest">
                          <span>Negative (-1)</span>
                          <span>Positive (1)</span>
                        </div>
                        <div className="w-full bg-black/40 rounded-full h-4 overflow-hidden border border-white/5">
                          <div 
                            className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 transition-all rounded-full" 
                            style={{width: `${((insight.sentiment_score + 1) / 2) * 100}%`}}
                          />
                        </div>
                        <div className="text-right text-xs text-primary font-bold">
                          Score: {insight.sentiment_score.toFixed(2)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {activeTab === 'recommendations' && (
                <div className="animate-in fade-in slide-in-from-bottom-2">
                  <h3 className="font-serif text-xl font-bold mb-6 text-primary">You Might Also Like</h3>
                  {recs.length > 0 ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {recs.map((r: any) => (
                        <Link href={`/books/${r.id}`} key={r.id} className="group flex flex-col gap-3">
                          <div className="aspect-[2/3] overflow-hidden rounded-lg bg-black/40 border border-white/10 relative shadow-lg">
                            {r.cover_image_url ? (
                              <img src={r.cover_image_url} alt={r.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-xs text-textMuted">No Cover</div>
                            )}
                            {r.relevance_score !== undefined && (
                              <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-md text-primary text-[10px] px-2 py-1 font-bold rounded border border-primary/30">
                                {Math.round(r.relevance_score * 100)}% Match
                              </div>
                            )}
                          </div>
                          <p className="text-sm font-bold line-clamp-2 leading-tight group-hover:text-primary transition-colors">{r.title}</p>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-textMuted italic">No recommendations available. Try adding more books!</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
