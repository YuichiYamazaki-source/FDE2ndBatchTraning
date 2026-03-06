import { proxyImageUrl } from '../api/client'
import Breadcrumb from './Breadcrumb'

export default function ProductCard({ product, onClick }) {
  const {
    product_name,
    description,
    main_image,
    product_id,
    final_price,
    rating,
    brand,
    available_for_delivery,
    available_for_pickup,
    category_name,
    root_category_name,
  } = product

  return (
    <article
      onClick={() => onClick(product)}
      style={{ background: '#fff', borderRadius: 8, padding: 16, cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.1)', display: 'flex', gap: 12 }}
      aria-label={product_name}
    >
      {main_image && (
        <img src={proxyImageUrl(main_image)} alt={product_name} style={{ width: 80, height: 80, objectFit: 'contain', borderRadius: 4, flexShrink: 0 }} />
      )}
      <div style={{ flex: 1, minWidth: 0 }}>
        <Breadcrumb rootCategory={root_category_name} category={category_name} productName={product_name} />
        <h3 style={{ margin: '4px 0', fontSize: 15, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{product_name}</h3>
        <p style={{ fontSize: 13, color: '#555', margin: '2px 0', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{description}</p>
        <div style={{ display: 'flex', gap: 12, marginTop: 6, fontSize: 13, flexWrap: 'wrap' }}>
          <span><strong>${final_price?.toFixed(2) ?? '—'}</strong></span>
          {rating != null && <span>⭐ {rating}</span>}
          {brand && <span style={{ color: '#888' }}>{brand}</span>}
          <span style={{ color: available_for_delivery ? '#2a7' : '#aaa' }}>
            {available_for_delivery ? '✓ Delivery' : '✗ Delivery'}
          </span>
          <span style={{ color: available_for_pickup ? '#2a7' : '#aaa' }}>
            {available_for_pickup ? '✓ Pickup' : '✗ Pickup'}
          </span>
        </div>
        <div style={{ fontSize: 11, color: '#bbb', marginTop: 4 }}>ID: {product_id}</div>
      </div>
    </article>
  )
}
