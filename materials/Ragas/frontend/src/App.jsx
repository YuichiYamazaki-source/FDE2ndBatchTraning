import { useState } from 'react'
import SearchBar from './components/SearchBar'
import ProductList from './components/ProductList'
import ProductDetail from './components/ProductDetail'
import ChatPanel from './components/ChatPanel'
import { searchProducts, getProduct } from './api/client'

export default function App() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [detailProduct, setDetailProduct] = useState(null)

  async function handleSearch(query, limit) {
    setLoading(true)
    setError(null)
    try {
      const data = await searchProducts(query, limit)
      setResults(data.results)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleSelectProduct(product) {
    try {
      const detail = await getProduct(product.product_id)
      setDetailProduct(detail)
      setSelectedProduct(product)
    } catch {
      // fallback: show summary data
      setDetailProduct(product)
      setSelectedProduct(product)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
      <h1 style={{ fontSize: 22, marginBottom: 16 }}>Product Discovery</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <p style={{ color: 'red', marginTop: 8, fontSize: 13 }}>{error}</p>}
      <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 20 }}>
        <ProductList products={results} onSelect={handleSelectProduct} />
        <ChatPanel selectedProductId={selectedProduct?.product_id ?? null} />
      </div>
      {detailProduct && <ProductDetail product={detailProduct} onClose={() => setDetailProduct(null)} />}
    </div>
  )
}
