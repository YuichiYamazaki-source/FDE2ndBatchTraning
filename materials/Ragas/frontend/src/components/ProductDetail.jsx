import { proxyImageUrl } from '../api/client'
import Breadcrumb from './Breadcrumb'

export default function ProductDetail({ product, onClose }) {
  if (!product) return null

  const {
    product_name, description, main_image, product_id,
    final_price, unit_price, currency, rating, review_count,
    brand, category_name, root_category_name,
    available_for_delivery, available_for_pickup,
    specifications, ingredients, colors,
    customer_reviews, seller,
  } = product

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }} onClick={onClose}>
      <div style={{ background: '#fff', borderRadius: 10, padding: 24, maxWidth: 640, width: '90%', maxHeight: '85vh', overflowY: 'auto' }} onClick={e => e.stopPropagation()}>
        <button onClick={onClose} aria-label="Close" style={{ float: 'right', background: 'none', border: 'none', fontSize: 20, cursor: 'pointer' }}>✕</button>
        <Breadcrumb rootCategory={root_category_name} category={category_name} productName={product_name} />
        <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
          {main_image && <img src={proxyImageUrl(main_image)} alt={product_name} style={{ width: 120, height: 120, objectFit: 'contain' }} />}
          <div>
            <h2 style={{ fontSize: 18 }}>{product_name}</h2>
            {brand && <p style={{ color: '#888', fontSize: 13 }}>{brand}</p>}
            <p style={{ marginTop: 4 }}><strong>${final_price?.toFixed(2)}</strong>{unit_price && unit_price !== final_price && <span style={{ fontSize: 12, color: '#999', marginLeft: 6 }}>({currency} {unit_price}/unit)</span>}</p>
            {rating != null && <p style={{ fontSize: 13 }}>⭐ {rating} ({review_count} reviews)</p>}
            <p style={{ fontSize: 13, marginTop: 4 }}>
              {available_for_delivery ? '✓ Delivery' : '✗ Delivery'} &nbsp;
              {available_for_pickup ? '✓ Pickup' : '✗ Pickup'}
            </p>
          </div>
        </div>
        {description && <Section title="Description">{description}</Section>}
        {specifications && <SpecificationsSection data={specifications} />}
        {ingredients && <Section title="Ingredients">{ingredients}</Section>}
        {colors && <ColorsSection data={colors} />}
        {seller && <Section title="Seller">{seller}</Section>}
        {customer_reviews && <ReviewsSection data={customer_reviews} />}
        <p style={{ fontSize: 11, color: '#ccc', marginTop: 16 }}>Product ID: {product_id}</p>
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div style={{ marginTop: 14 }}>
      <h4 style={{ fontSize: 13, fontWeight: 600, color: '#555', marginBottom: 4 }}>{title}</h4>
      <p style={{ fontSize: 13, lineHeight: 1.6 }}>{children}</p>
    </div>
  )
}

function tryParseJson(data) {
  if (Array.isArray(data)) return data
  if (typeof data !== 'string') return null
  try { return JSON.parse(data) } catch { return null }
}

function SpecificationsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 14 }}>
      <h4 style={{ fontSize: 13, fontWeight: 600, color: '#555', marginBottom: 4 }}>Specifications</h4>
      <table style={{ fontSize: 13, borderCollapse: 'collapse', width: '100%' }}>
        <tbody>
          {items.map((spec, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '4px 8px 4px 0', color: '#777', whiteSpace: 'nowrap', verticalAlign: 'top' }}>{spec.name}</td>
              <td style={{ padding: '4px 0' }}>{spec.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ColorsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 14 }}>
      <h4 style={{ fontSize: 13, fontWeight: 600, color: '#555', marginBottom: 4 }}>Colors</h4>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {items.map((color, i) => (
          <span key={i} style={{ fontSize: 12, padding: '2px 10px', borderRadius: 12, background: '#f0f0f0', color: '#444' }}>{color}</span>
        ))}
      </div>
    </div>
  )
}

function ReviewsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 14 }}>
      <h4 style={{ fontSize: 13, fontWeight: 600, color: '#555', marginBottom: 4 }}>Customer Reviews</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {items.map((rev, i) => (
          <div key={i} style={{ background: '#fafafa', borderRadius: 6, padding: '8px 12px', fontSize: 13 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>{rev.name || 'Anonymous'}</span>
              <span style={{ color: '#e8a000' }}>{'★'.repeat(rev.rating || 0)}{'☆'.repeat(5 - (rev.rating || 0))}</span>
            </div>
            {rev.title && <p style={{ fontWeight: 500, margin: '0 0 2px' }}>{rev.title}</p>}
            <p style={{ margin: 0, color: '#555', lineHeight: 1.5 }}>{rev.review}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
