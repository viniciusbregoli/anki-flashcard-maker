import { useState } from 'react';
import { Sparkles, Download, Layers, Volume2, Type, ArrowRight, Zap, AlertCircle, ChevronLeft, ChevronRight, RefreshCw, Loader2 } from 'lucide-react';

const CARDS_PER_PAGE = 6;

function App() {
  const [inputWords, setInputWords] = useState('');
  const [cards, setCards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [progress, setProgress] = useState(0);
  const [currentWord, setCurrentWord] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [regeneratingId, setRegeneratingId] = useState(null);

  // Derived state for pagination
  const totalPages = Math.ceil(cards.length / CARDS_PER_PAGE);
  const currentCards = cards.slice(
    (currentPage - 1) * CARDS_PER_PAGE,
    currentPage * CARDS_PER_PAGE
  );

  const handleGenerate = async () => {
    if (!inputWords.trim()) return;

    setIsLoading(true);
    setError(null);
    setCards([]);
    setProgress(0);
    setCurrentWord('');
    setCurrentPage(1);

    const words = inputWords.split('\n').map(w => w.trim()).filter(w => w.length > 0);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ words }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate cards. Please check the backend.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            try {
              const data = JSON.parse(jsonStr);

              if (data.type === 'progress') {
                setProgress(data.percent);
                setCurrentWord(data.word);
              } else if (data.type === 'result') {
                setCards(data.cards);
                setProgress(100);
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerateCard = async (cardToRegenerate) => {
    try {
      setRegeneratingId(cardToRegenerate.id);

      // We will re-use the 'source' as the word. If the card was previously modified (e.g. stripped article), 
      // this might send "Tisch" instead of "Der Tisch". This is usually fine as it regenerates correctly.
      const response = await fetch('/api/regenerate-card', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          word: cardToRegenerate.source,
          id: cardToRegenerate.id
        }),
      });

      if (!response.ok) throw new Error('Failed to regenerate');

      const data = await response.json();

      if (data.status === 'success') {
        setCards(prevCards => prevCards.map(c => c.id === cardToRegenerate.id ? data.card : c));
      }

    } catch (err) {
      console.error("Regeneration failed", err);
    } finally {
      setRegeneratingId(null);
    }
  };

  const handleDownload = () => {
    window.location.href = '/api/download';
  };

  return (
    <div className="app-container">

      {/* Header */}
      <header className="hero-header">
        <div className="logo-badge">
          <Sparkles size={16} />
          <span>AI-Powered Flashcards</span>
        </div>
        <h1 className="main-title">
          AnkiGen.ai
        </h1>
        <p className="subtitle">
          Turn German vocabulary into Anki cards instantly. <br />
          Translations, gender, context & audio included.
        </p>
      </header>

      <main className="main-content">

        {/* Input Section */}
        <section className="input-section">
          <div className="glass-panel input-panel">
            <div className="panel-header">
              <h2 className="section-title">
                <Layers className="icon-violet" size={20} />
                Input
              </h2>
              <span className="helper-text">One item per line</span>
            </div>

            <textarea
              className="main-textarea"
              placeholder={`Hauptbahnhof\nWie geht es dir?\nder Apfel`}
              value={inputWords}
              onChange={(e) => setInputWords(e.target.value)}
            />

            {error && (
              <div className="error-banner">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            {isLoading && (
              <div className="progress-container animate-fade-in">
                <div className="flex justify-between text-sm mb-2 text-slate-300">
                  <span className="font-mono text-xs truncate">{currentWord || 'Initializing...'}</span>
                </div>

                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>

                <div className="flex justify-end mt-2">
                  <span className="font-bold text-violet-400 text-sm">{progress}%</span>
                </div>
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={isLoading || !inputWords.trim()}
              className="primary-btn full-width"
            >
              {isLoading ? (
                <>
                  <div className="spinner" />
                  Processing...
                </>
              ) : (
                <>
                  <Zap size={18} /> Generate Cards
                </>
              )}
            </button>
          </div>
        </section>

        {/* Results Section */}
        <section className="results-section">
          <div className="results-header">
            <div>
              <h2 className="section-title">
                <Layers className="icon-cyan" size={20} />
                Generated Cards
              </h2>
              <p className="helper-text mt-1">
                {cards.length > 0 ? `${cards.length} cards ready` : 'No cards generated yet'}
              </p>
            </div>

            {cards.length > 0 && (
              <button onClick={handleDownload} className="primary-btn secondary-action">
                <Download size={18} /> Download Package (.apkg)
              </button>
            )}
          </div>

          <div className="cards-grid">
            {currentCards.map((card) => (
              <div key={card.id} className="glass-panel flashcard animate-fade-in relative">
                <div className="card-header">
                  <div className="card-title-group">
                    {card.gender && card.gender !== 'N/A' && (
                      <span className={`badge badge-${card.gender}`}>
                        {card.gender}
                      </span>
                    )}
                    <div className="flex items-baseline gap-2 cursor-pointer group" onClick={() => {
                      if (card.audio) {
                        new Audio(`/api/audio/${card.audio}?t=${Date.now()}`).play();
                      }
                    }}>
                      <div className="flex items-center gap-2">
                        <h3 className="card-word group-hover:text-violet-400 transition-colors">{card.source}</h3>
                        {card.audio && <Volume2 size={18} className="icon-muted group-hover:text-violet-400" />}
                      </div>
                      {card.plural && card.plural !== 'N/A' && (
                        <span className="text-slate-500 text-sm font-mono">(pl: {card.plural})</span>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRegenerateCard(card);
                    }}
                    className="p-2 text-slate-500 hover:text-violet-400 disabled:opacity-50 transition-colors rounded-full hover:bg-slate-800/50 ml-auto"
                    disabled={regeneratingId !== null}
                    title="Regenerate this card"
                  >
                    {regeneratingId === card.id ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <RefreshCw size={16} />
                    )}
                  </button>
                </div>

                <p className="card-translation">
                  {card.translation.join(', ')}
                </p>

                {card.context && card.context[0] && card.context[0].german !== 'N/A' && (
                  <div className="context-box mt-auto">
                    <p className="context-de">"{card.context[0].german}"</p>
                    <p className="context-en">{card.context[0].english}</p>
                  </div>
                )}

                {card.tip && (
                  <div className="tip-box mt-3">
                    <div className="flex gap-2 items-start text-sm text-yellow-200/80">
                      <div className="mt-1"><AlertCircle size={14} className="text-yellow-400" /></div>
                      <p className="m-0 italic">{card.tip}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {cards.length === 0 && !isLoading && (
              <div className="empty-state">
                <Type size={48} className="icon-faded" />
                <p>Enter words and click generate to see preview</p>
              </div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination-controls">
              <button
                className="icon-btn"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft size={20} />
              </button>
              <span className="pagination-text">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="icon-btn"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 AnkiGen. Built with Python & React.</p>
      </footer>
    </div>
  );
}

export default App;
