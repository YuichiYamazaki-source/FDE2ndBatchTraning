import { render, screen } from '@testing-library/react'
import Breadcrumb from '../components/Breadcrumb'

describe('Breadcrumb', () => {
  it('renders Home always', () => {
    render(<Breadcrumb />)
    expect(screen.getByText('Home')).toBeInTheDocument()
  })

  it('renders full path when all props provided', () => {
    render(<Breadcrumb rootCategory="Beauty" category="Skincare" productName="Face Cream" />)
    expect(screen.getByText('Beauty')).toBeInTheDocument()
    expect(screen.getByText('Skincare')).toBeInTheDocument()
    expect(screen.getByText('Face Cream')).toBeInTheDocument()
  })

  it('skips missing segments', () => {
    render(<Breadcrumb rootCategory="Beauty" />)
    expect(screen.getByText('Beauty')).toBeInTheDocument()
    expect(screen.queryByText('Skincare')).not.toBeInTheDocument()
  })
})
