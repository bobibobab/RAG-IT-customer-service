import React, { useState } from 'react';
import { Search, Loader2, HelpCircle } from 'lucide-react';

interface SearchResult {
  question: string;
  similarity: number;
  answer: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [AIanswer, setAIanswer] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 3,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }

      const data = await response.json();
      console.log(data)
      setResults(data.results);
      setAIanswer(data.gpt_answer.summary)
    } catch (err) {
      setError('An error occurred while searching. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <HelpCircle className="w-12 h-12 text-blue-600 animate-pulse" />
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            IT Customer Support Search
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Find instant answers to your questions
          </p>
        </div>

        <form onSubmit={handleSearch} className="mb-12">
          <div className="flex gap-3">
            <div className="flex-1 relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg blur opacity-30 group-hover:opacity-40 transition-opacity"></div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your question here..."
                className="relative w-full px-6 py-4 rounded-lg border-2 border-transparent bg-white shadow-lg focus:border-blue-500 outline-none transition-all duration-300 text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg flex items-center gap-2 min-w-[140px] justify-center"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              Search
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-6 mb-8 animate-fade-in">
            <p className="text-red-800 flex items-center gap-2">
              <span className="font-medium">Error:</span> {error}
            </p>
          </div>
        )}

        {isLoading ? (
          <div className="space-y-6">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="bg-white rounded-xl p-8 shadow-lg animate-pulse"
              >
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          results.length > 0 && (
            <div className="space-y-6">
              {/* Show GPT Answer First */}
                {AIanswer && (
                <div className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Answer</h3>
                    <p className="text-gray-700 leading-relaxed">{AIanswer}</p>
                </div>
              )}

              {/* Show Related Questions and Answers */}
                <div className="space-y-6">
                  {results.map((result, index) => (
                    <div
                      key={index}
                      className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100"
                    >
                      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Related Question and Answer {index + 1}</h1> {/* 제목 강조 */}
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">
                        {result.question}
                      </h3>
                      <div className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-4">
                        Similarity: {result.similarity.toFixed(4)}
                      </div>
                      <p className="text-gray-700 leading-relaxed">{result.answer}</p>
                    </div>
                  ))}
                </div>

            </div>
          )
        )}

        {!isLoading && !error && results.length === 0 && query && (
          <div className="text-center py-16">
            <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-100">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-xl text-gray-600">
                No results found. Try a different search term.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;