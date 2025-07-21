import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Define types for props and state
interface Point {
  lat: number;
  lon: number;
}

interface SearchResult {
  name: string;
  category: string;
  address: string; // Add address field
  location: Point;
}

interface SearchComponentProps {
  onPlaceSelect: (point: Point) => void;
}

const SearchComponent: React.FC<SearchComponentProps> = ({ onPlaceSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    const delayDebounceFn = setTimeout(() => {
      setLoading(true);
      axios.get(`http://127.0.0.1:8000/search?q=${query}`)
        .then(response => {
          setResults(response.data.results);
        })
        .catch(error => {
          console.error("Error fetching search results:", error);
        })
        .finally(() => {
          setLoading(false);
        });
    }, 500); // 500ms debounce delay

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const handleSelect = (result: SearchResult) => {
    setQuery('');
    setResults([]);
    onPlaceSelect(result.location);
  };

  return (
    <div className="search-container">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for a place..."
      />
      {loading && <p>Loading...</p>}
      {results.length > 0 && (
        <ul className="search-results">
          {results.map((result, index) => (
            <li key={index} onClick={() => handleSelect(result)}>
              <strong>{result.name}</strong>
              <p>{result.category}</p>
              {result.address && <p>{result.address}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchComponent;
