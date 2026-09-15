import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { App } from './App'

describe('App', () => {
  it('introduces API Doctor and its security boundary', () => {
    render(<App />)
    expect(
      screen.getByRole('heading', { level: 1, name: 'API Doctor' }),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/outbound requests stay disabled/i),
    ).toBeInTheDocument()
  })
})
