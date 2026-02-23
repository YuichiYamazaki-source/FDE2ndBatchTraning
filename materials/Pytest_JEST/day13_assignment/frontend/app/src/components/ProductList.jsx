import { useState, useEffect } from "react";
import axios from "axios";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    axios.get("http://localhost:8000/products")
      .then(res => {
        setProducts(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch products");
        setLoading(false);
      });
  }, []);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (products.length === 0) return <p>product found</p>;
  
  return (
    <ul>
      {products.map((product, index) => (
      <li key={index}>
        {product.name} - ${product.price} - {product.category}
      </li>
    ))}
    </ul>
  );
}

export default ProductList;