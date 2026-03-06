import { render, screen, fireEvent } from '@testing-library/react'
import SearchBar from '../components/SearchBar'

describe('SearchBar', () => {
  it('renders input and button', () => {
    render(<SearchBar onSearch={() => {}} loading={false} />)
    expect(screen.getByLabelText('Search query')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument()
  })

  it('calls onSearch with query and limit on submit', () => {
    const onSearch = vi.fn()
    render(<SearchBar onSearch={onSearch} loading={false} />)
    fireEvent.change(screen.getByLabelText('Search query'), { target: { value: 'organic skincare' } })
    fireEvent.submit(screen.getByRole('button').closest('form'))
    expect(onSearch).toHaveBeenCalledWith('organic skincare', 10)
  })

  it('disables button when loading', () => {
    render(<SearchBar onSearch={() => {}} loading={true} />)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('disables button when query is empty', () => {
    render(<SearchBar onSearch={() => {}} loading={false} />)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('limit input has min=1 max=15', () => {
    render(<SearchBar onSearch={() => {}} loading={false} />)
    const limitInput = screen.getByLabelText('Result limit')
    expect(limitInput).toHaveAttribute('min', '1')
    expect(limitInput).toHaveAttribute('max', '15')
  })
})
