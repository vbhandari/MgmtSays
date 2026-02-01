import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/utils';
import Badge from './Badge';

describe('Badge', () => {
  it('renders with text', () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders default variant', () => {
    render(<Badge variant="default">Default</Badge>);
    expect(screen.getByText('Default')).toHaveClass('bg-gray-100');
  });

  it('renders primary variant', () => {
    render(<Badge variant="primary">Primary</Badge>);
    expect(screen.getByText('Primary')).toHaveClass('bg-blue-100');
  });

  it('renders success variant', () => {
    render(<Badge variant="success">Success</Badge>);
    expect(screen.getByText('Success')).toHaveClass('bg-green-100');
  });

  it('renders warning variant', () => {
    render(<Badge variant="warning">Warning</Badge>);
    expect(screen.getByText('Warning')).toHaveClass('bg-yellow-100');
  });

  it('renders danger variant', () => {
    render(<Badge variant="danger">Danger</Badge>);
    expect(screen.getByText('Danger')).toHaveClass('bg-red-100');
  });

  it('renders info variant', () => {
    render(<Badge variant="info">Info</Badge>);
    expect(screen.getByText('Info')).toHaveClass('bg-indigo-100');
  });

  it('renders small size', () => {
    render(<Badge size="sm">Small</Badge>);
    expect(screen.getByText('Small')).toHaveClass('text-xs');
  });

  it('renders medium size', () => {
    render(<Badge size="md">Medium</Badge>);
    expect(screen.getByText('Medium')).toHaveClass('text-sm');
  });
});
