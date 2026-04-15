'use client';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import BookCard from '@/components/BookCard';

export default function Home() {
  const [books, setBooks] = useState<any[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [search, setSearch] = useState('');
  const [genre, setGenre] = useState('');
  const [ordering, setOrdering] = useState('-scraped_at');
  const [scraping, setScraping] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('https://books.toscrape.com');
  const [pages, setPages] = useState(1);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const g = await api.books.genres();
      setGenres(g);
      
      const params: any = {};
      if (search) params.search = search;
      if (genre) params.genre = genre;
      if (ordering) params.ordering = ordering;
      
      const res = await api.books.list(params);
      setBooks(res.results || res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchBooks();
    }, 500);
    return () => clearTimeout(delayDebounce);
  }, [search, genre, ordering]);

  const handleScrape = async () => {
    if (scraping) return;
    setScraping(true);
    try {
      const r = await api.books.scrape(scrapeUrl, pages);
      alert(`Scraping started! Task ID: ${r.task_id}`);
    } catch(e) {
      alert("Error starting scrape");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <section className="text-center py-12 px-4 glass-card from-primary/5 to-transparent bg-gradient-to-b border-primary/20">
        <h1 className="font-serif text-5xl md:text-6xl font-bold mb-4 text-textMain glow-text">
          Discover Books with <span className="text-primary italic">AI</span>
        </h1>
        <p className="text-textMuted text-lg max-w-2xl mx-auto mb-8">
          Intelligent document parsing, genre classification, and RAG-based Q&A for an unparalleled reading discovery experience.
        </p>
        
        <div className="flex flex-wrap justify-center gap-4 items-center bg-black/20 p-4 rounded-xl border border-white/5 inline-flex backdrop-blur">
          <input 
            type="text" 
            value={scrapeUrl}
            onChange={e => setScrapeUrl(e.target.value)}
            className="bg-transparent border-b border-white/20 focus:border-primary outline-none px-2 py-1 text-sm text-textMain min-w-[250px]"
            placeholder="URL to scrape"
          />
          <input 
            type="number" 
            value={pages}
            onChange={e => setPages(parseInt(e.target.value))}
            className="bg-transparent border-b border-white/20 focus:border-primary outline-none px-2 py-1 text-sm text-textMain w-[60px] text-center"
            min={1} max={10}
          />
          <button 
            onClick={handleScrape}
            disabled={scraping}
            className="bg-primary text-background px-4 py-1.5 rounded font-bold text-sm tracking-wide disabled:opacity-50"
          >
            {scraping ? 'Starting...' : 'Scrape More Books'}
          </button>
        </div>
      </section>

      <section className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row gap-4 glass-card p-4">
          <input 
            type="text" 
            placeholder="Search by title or author..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 bg-black/20 border border-white/10 rounded px-4 py-2 focus:border-primary focus:outline-none transition-colors"
          />
          <select 
            value={genre}
            onChange={e => setGenre(e.target.value)}
            className="bg-black/20 border border-white/10 rounded px-4 py-2 focus:border-primary focus:outline-none transition-colors"
          >
            <option value="">All Genres</option>
            {genres.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
          <select 
            value={ordering}
            onChange={e => setOrdering(e.target.value)}
            className="bg-black/20 border border-white/10 rounded px-4 py-2 focus:border-primary focus:outline-none transition-colors"
          >
            <option value="-scraped_at">Newest</option>
            <option value="-rating">Top Rated</option>
            <option value="title">Title A-Z</option>
          </select>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[1,2,3,4,5,6,7,8].map(i => (
              <div key={i} className="glass-card h-96 animate-pulse bg-white/5"></div>
            ))}
          </div>
        ) : books.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {books.map(b => <BookCard key={b.id} book={b} />)}
          </div>
        ) : (
          <div className="text-center py-20 glass-card">
            <h3 className="font-serif text-2xl text-textMuted">No books found.</h3>
            <p className="text-sm mt-2 text-white/50">Try scraping some books from the hero section!</p>
          </div>
        )}
      </section>
    </div>
  );
}
