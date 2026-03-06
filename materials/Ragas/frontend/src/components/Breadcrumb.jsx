export default function Breadcrumb({ rootCategory, category, productName }) {
  const parts = [
    { label: 'Home', key: 'home' },
    rootCategory && { label: rootCategory, key: 'root' },
    category && { label: category, key: 'cat' },
    productName && { label: productName, key: 'product' },
  ].filter(Boolean)

  return (
    <nav aria-label="breadcrumb" style={{ fontSize: 13, color: '#666' }}>
      {parts.map((part, i) => (
        <span key={part.key}>
          {i > 0 && <span style={{ margin: '0 6px' }}>{'>'}</span>}
          <span>{part.label}</span>
        </span>
      ))}
    </nav>
  )
}
