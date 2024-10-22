import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  createTracker,
  trackPageView,
  trackSearch,
  trackSearchClick
} from "@elastic/behavioral-analytics-javascript-tracker";

createTracker({
  endpoint: "endpoint",
  collectionName: "tracking-search",
  apiKey: "key"
});

const Facets = ({ categories = [], productTypes = [], brands = [], selectedFacets, onFacetChange }) => {
  return (
    <div className="facets">
      <h3>Filters</h3>

      <h4>Categories</h4>
      {categories.map((facet, index) => (
        <div key={`category-${index}`} className="facet-item">
          <input
            type="checkbox"
            checked={selectedFacets.categories.includes(facet.category)}
            onChange={() => onFacetChange('categories', facet.category)}
          />
          <label>{facet.category || "Outros"} ({facet.count})</label>
        </div>
      ))}

      <h4>Brands</h4>
      {brands.map((facet, index) => (
        <div key={`category-${index}`} className="facet-item">
          <input
            type="checkbox"
            checked={selectedFacets.brands.includes(facet.brand)}
            onChange={() => onFacetChange('brands', facet.brand)}
          />
          <label>{facet.brand || "Outros"} ({facet.count})</label>
        </div>
      ))}

      <h4>Types</h4>
      {productTypes.map((facet, index) => (
        <div key={`product-type-${index}`} className="facet-item">
          <input
            type="checkbox"
            checked={selectedFacets.productTypes.includes(facet.product_type)}
            onChange={() => onFacetChange('productTypes', facet.product_type)}
          />
          <label>{facet.product_type} ({facet.count})</label>
        </div>
      ))}
    </div>
  );
};

const SearchBar = ({ searchQuery, setSearchQuery, onSearch, isHybridSearch, setIsHybridSearch }) => {
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Buscar produtos..."
        value={searchQuery}
        onKeyDown={handleKeyDown}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button onClick={onSearch}>Pesquisar</button>
      <div className="hybrid-search-checkbox">
        <label>
          <input
            type="checkbox"
            checked={isHybridSearch}
            onChange={(e) => setIsHybridSearch(e.target.checked)}
          />
          Hybrid Search
        </label>
      </div>
    </div>
  );
};


const ProductCard = ({ product, searchTerm, products }) => {
  const defaultImage = "https://via.placeholder.com/100";

  const handleClick = () => {
    //alert(`Produto: ${product.name} - Termo de pesquisa: ${searchTerm}`);

    trackSearchClick({
      document: { id: product.id, index: "products-catalog"},
      search: {
        query: searchTerm,
        page: {
          current: 1,
          size: products.length,
        },
        results: {
          items: [
            {
              document: {
                id: product.id,
                index: "products-catalog",
              }
            },
          ],
          total_results: products.length,
        },
        search_application: "app-product-store"
      },
    });
  };

  return (
    <div className="product-card" onClick={handleClick}>
      <div className="product-image">
        <img
          src={product.image_link}
          alt={product.name}
          onError={(e) => e.target.src = defaultImage}
        />
      </div>
      <div className="product-info">
        <h4>{product.name}</h4>
        <p>{product.description}</p>
        <p>{product.brand}</p>
        <span className="product-price">
          {product.currency ? product.currency : 'USD'} {parseFloat(product.price).toFixed(2)}
        </span>
        <div className="product-tags">
          {product.tags && product.tags.map((tag, index) => (
            <span key={index} className={`tag tag-${index % 5}`}>{tag}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

const ProductList = ({ products, searchTerm }) => {
  return (
    <div className="product-list">
      {Array.isArray(products) && products.length > 0 ? (
        products.map(product => (
          <ProductCard key={product.id} product={product} searchTerm={searchTerm} products={products} />
        ))
      ) : (
        <p>Nenhum produto encontrado</p>
      )}
    </div>
  );
};


const ProductPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [facets, setFacets] = useState({ categories: [], product_types: [] });
  const [selectedFacets, setSelectedFacets] = useState({
    categories: [],
    productTypes: [],
    brands: []
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [isHybridSearch, setIsHybridSearch] = useState(false);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/products/search`, {
        params: {
          query: searchTerm,
          selectedCategories: selectedFacets.categories,
          selectedProductTypes: selectedFacets.productTypes,
          selectedbrands: selectedFacets.brands,
          hybrid: isHybridSearch
        }
      });
      setProducts(response.data);
      const documents = products.map(product => ({
        document: {
          id: product.id,
          index: "products-catalog"
        }
      }));
      trackSearch({
        search: {
          query: searchTerm,
          results: {
            items: documents,
            total_results: response.data.length,
          },
        },
      });
    } catch (error) {
      console.error('Erro ao buscar produtos', error);
    }
  };

  // Função para buscar os facets
  const fetchFacets = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/products/facets`, {
        params: {
          query: searchTerm,
          selectedCategories: selectedFacets.categories,
          selectedProductTypes: selectedFacets.productTypes,
          selectedbrands: selectedFacets.brands,
          hybrid: isHybridSearch
        }
      });
      setFacets(response.data);
    } catch (error) {
      console.error('Erro ao buscar facets', error);
    }
  };

  useEffect(() => {
    fetchFacets();
    fetchProducts();
    trackPageView({
      page: {
        title: "home-page"
      },
    });
  }, [isHybridSearch, searchTerm, selectedFacets]);

  const handleSearch = () => {
    setSearchTerm(searchQuery);
    fetchProducts();
  };

  const handleFacetChange = (facetType, facetId) => {
    setSelectedFacets(prevState => {
      const selected = prevState[facetType].includes(facetId)
        ? prevState[facetType].filter(id => id !== facetId)
        : [...prevState[facetType], facetId];

      return {
        ...prevState,
        [facetType]: selected
      };
    });
  };

  return (
    <div className="product-page">
      <div className="search-and-facets">
        <Facets
          categories={facets.categories}
          productTypes={facets.product_types}
          brands={facets.brands}
          selectedFacets={selectedFacets}
          onFacetChange={handleFacetChange}
        />
      </div>

      <div className="product-section">
        <SearchBar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearch={handleSearch}
          isHybridSearch={isHybridSearch}
          setIsHybridSearch={setIsHybridSearch}
        />
        <ProductList products={products} searchTerm={searchTerm} />
      </div>
    </div>
  );
};

export default ProductPage;

