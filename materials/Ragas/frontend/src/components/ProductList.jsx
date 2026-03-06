import ProductCard from './ProductCard'

export default function ProductList({ products, onSelect }) {
  if (!products.length) return null

  return (
    <section>
      <p style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>{products.length} result{products.length !== 1 ? 's' : ''}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {products.map(p => (
          <ProductCard key={p.product_id} product={p} onClick={onSelect} />
        ))}
      </div>
    </section>
  )
}
