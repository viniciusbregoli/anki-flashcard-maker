import { useState } from 'react';
import { Sparkles, Download, Layers, Volume2, Type, ArrowRight, Zap, AlertCircle } from 'lucide-react';

function App() {
  const [inputWords, setInputWords] = useState('');
  const [cards, setCards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!inputWords.trim()) return;

    setIsLoading(true);
    setError(null);
    setCards([]);

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

      const data = await response.json();
      setCards(data.cards);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
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
            {cards.map((card) => (
              <div key={card.id} className="glass-panel flashcard animate-fade-in">
                <div className="card-header">
                  <div className="card-title-group">
                    {card.gender && card.gender !== 'N/A' && (
                      <span className={`badge badge-${card.gender}`}>
                        {card.gender}
                      </span>
                    )}
                    <div className="flex items-baseline gap-2 cursor-pointer group" onClick={() => {
                      if (card.audio) {
                        new Audio(`/api/audio/${card.audio}`).play();
                      }
                    }}>
                      <div className="flex items-center gap-2">
                        <h3 className="card-word group-hover:text-violet-400 transition-colors">{card.source}</h3>
                        {card.input_type === 'word' && <Volume2 size={18} className="icon-muted group-hover:text-violet-400" />}
                      </div>
                      {card.plural && card.plural !== 'N/A' && (
                        <span className="text-slate-500 text-sm font-mono">(pl: {card.plural})</span>
                      )}
                    </div>
                  </div>
                </div>

                <p className="card-translation">
                  {card.translation.join(', ')}
                </p>

                {card.context && card.context[0] && card.context[0].german !== 'N/A' && (
                  <div className="context-box">
                    <p className="context-de">"{card.context[0].german}"</p>
                    <p className="context-en">{card.context[0].english}</p>
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
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 AnkiGen. Built with Python & React.</p>
      </footer>
    </div>
  );
}

export default App;
