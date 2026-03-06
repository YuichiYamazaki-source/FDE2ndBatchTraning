const BASE_URL = '/api'

export function proxyImageUrl(url) {
  if (!url) return null
  const clean = url.replace(/^"|"$/g, '')
  if (clean.startsWith('https://i5.walmartimages.com/')) {
    return `${BASE_URL}/image-proxy?url=${encodeURIComponent(clean)}`
  }
  return clean
}

export async function searchProducts(query, limit = 10) {
  const res = await fetch(`${BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit }),
  })
  if (!res.ok) throw new Error(`Search failed: ${res.status}`)
  return res.json()
}

export async function getProduct(productId) {
  const res = await fetch(`${BASE_URL}/products/${productId}`)
  if (!res.ok) throw new Error(`Product not found: ${res.status}`)
  return res.json()
}

export async function sendChat(message, productId = null) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, product_id: productId }),
  })
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`)
  return res.json()
}
