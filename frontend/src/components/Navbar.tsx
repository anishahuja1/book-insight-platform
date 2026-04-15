import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 glass-card mx-4 mt-4 px-6 md:px-12 py-4 flex justify-between items-center bg-background/80">
      <Link href="/" className="text-primary font-serif text-2xl font-bold tracking-wider">
        BookAI
      </Link>
      <div className="flex gap-6">
        <Link href="/" className="text-textMain hover:text-primary transition-colors text-sm font-medium uppercase tracking-widest">
          Library
        </Link>
        <Link href="/qa" className="text-textMain hover:text-primary transition-colors text-sm font-medium uppercase tracking-widest">
          Ask AI
        </Link>
      </div>
    </nav>
  );
}
