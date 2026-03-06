import { render, screen, fireEvent } from '@testing-library/react'
import ProductCard from '../components/ProductCard'

const PRODUCT = {
  product_id: '123',
  product_name: 'Organic Face Cream',
  description: 'A great moisturizer',
  main_image: '',
  final_price: 19.99,
  rating: 4.5,
  brand: 'NatureBrand',
  category_name: 'Skincare',
  root_category_name: 'Beauty',
  available_for_delivery: true,
  available_for_pickup: false,
}

describe('ProductCard', () => {
  it('renders product name as heading', () => {
    render(<ProductCard product={PRODUCT} onClick={() => {}} />)
    expect(screen.getByRole('heading', { name: 'Organic Face Cream' })).toBeInTheDocument()
  })

  it('shows price', () => {
    render(<ProductCard product={PRODUCT} onClick={() => {}} />)
    expect(screen.getByText('$19.99')).toBeInTheDocument()
  })

  it('shows delivery and pickup status', () => {
    render(<ProductCard product={PRODUCT} onClick={() => {}} />)
    expect(screen.getByText(/✓ Delivery/)).toBeInTheDocument()
    expect(screen.getByText(/✗ Pickup/)).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(<ProductCard product={PRODUCT} onClick={onClick} />)
    fireEvent.click(screen.getByRole('article'))
    expect(onClick).toHaveBeenCalledWith(PRODUCT)
  })
})
