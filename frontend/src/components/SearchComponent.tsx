import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { type Point } from '../types';

// Define types for props and state
interface SearchResult {
  name: string;
  category: string;
  address: string;
  location: Point;
}

interface SearchComponentProps {
  onPlaceSelect: (result: { name: string, location: Point }) => void;
}

const SearchComponent: React.FC<SearchComponentProps> = ({ onPlaceSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Debounced search
    if (query.length < 2) {
      setResults([]);
      return;
    }
    const delayDebounceFn = setTimeout(() => {
      setLoading(true);
      axios.get(`http://127.0.0.1:8000/search?q=${query}`)
        .then(response => setResults(response.data.results))
        .catch(error => console.error("Error fetching search results:", error))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (result: SearchResult) => {
    setQuery('');
    setResults([]);
    setIsFocused(false);
    onPlaceSelect({ name: result.name, location: result.location });
  };

  return (
    <div className="search-container" ref={searchContainerRef}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsFocused(true)}
        placeholder="장소 검색..."
      />

      {isFocused && query.length > 0 && (
        <ul className="search-results">
          {loading && <li className="loading-item">Loading...</li>}
          {!loading && results.length === 0 && query.length >= 2 && <li className="no-results-item">No results found.</li>}
          {results.map((result, index) => (
            <li key={index} onClick={() => handleSelect(result)}>
              <strong>{result.name}</strong>
              <p>{result.address}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchComponent;
