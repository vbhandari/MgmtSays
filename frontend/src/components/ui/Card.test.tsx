import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/utils';
import { Card, CardHeader, CardFooter } from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies default padding', () => {
    render(<Card>Content</Card>);
    const card = screen.getByText('Content').closest('.bg-white');
    expect(card).toHaveClass('p-6');
  });

  it('applies small padding', () => {
    render(<Card padding="sm">Content</Card>);
    const card = screen.getByText('Content').closest('.bg-white');
    expect(card).toHaveClass('p-4');
  });

  it('applies no padding', () => {
    render(<Card padding="none">Content</Card>);
    const card = screen.getByText('Content').closest('.bg-white');
    expect(card).toHaveClass('p-0');
  });

  it('adds hover effect when hover is true', () => {
    render(<Card hover>Content</Card>);
    const card = screen.getByText('Content').closest('.bg-white');
    expect(card).toHaveClass('hover:shadow-lg');
  });
});

describe('CardHeader', () => {
  it('renders title', () => {
    render(<CardHeader title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders subtitle', () => {
    render(<CardHeader title="Title" subtitle="Subtitle" />);
    expect(screen.getByText('Subtitle')).toBeInTheDocument();
  });

  it('renders action', () => {
    render(<CardHeader title="Title" action={<button>Action</button>} />);
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });
});

describe('CardFooter', () => {
  it('renders children', () => {
    render(<CardFooter>Footer content</CardFooter>);
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });
});
