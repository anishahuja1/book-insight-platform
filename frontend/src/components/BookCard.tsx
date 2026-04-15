import Link from 'next/link';

export default function BookCard({ book }: { book: any }) {
  return (
    <div className="glass-card flex flex-col h-full overflow-hidden group">
      <div className="h-64 overflow-hidden relative bg-black/20">
        {book.cover_image_url ? (
          <img 
            src={book.cover_image_url} 
            alt={book.title} 
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-textMuted font-serif">No Cover</div>
        )}
        <div className="absolute top-2 right-2 bg-black/60 backdrop-blur px-2 py-1 rounded text-xs font-bold text-primary border border-primary/20">
          ★ {book.rating || 'N/A'}
        </div>
      </div>
      <div className="p-5 flex flex-col flex-1">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-serif text-lg font-bold text-textMain line-clamp-2 leading-tight flex-1" title={book.title}>
            {book.title}
          </h3>
        </div>
        <p className="text-sm text-textMuted mb-3">By {book.author}</p>
        
        <div className="flex gap-2 mb-4 flex-wrap">
          {book.genre && (
            <span className="text-[10px] uppercase tracking-wider bg-white/10 px-2 py-1 rounded border border-white/5">
              {book.genre}
            </span>
          )}
          {book.reviews_count > 0 && (
            <span className="text-[10px] uppercase tracking-wider bg-white/10 px-2 py-1 rounded border border-white/5">
              {book.reviews_count} reviews
            </span>
          )}
        </div>
        
        <p className="text-sm text-textMuted line-clamp-3 mb-6 flex-1">
          {book.description || 'No description available.'}
        </p>
        
        <Link 
          href={`/books/${book.id}`}
          className="mt-auto w-full text-center py-2 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 rounded transition-colors font-medium text-sm tracking-wide"
        >
          View Details
        </Link>
      </div>
    </div>
  );
}
