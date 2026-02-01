import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/utils';
import { Alert } from './Alert';

describe('Alert', () => {
  it('renders with title', () => {
    render(<Alert title="Alert Title" />);
    expect(screen.getByText('Alert Title')).toBeInTheDocument();
  });

  it('renders with children', () => {
    render(<Alert>Alert message</Alert>);
    expect(screen.getByText('Alert message')).toBeInTheDocument();
  });

  it('renders info type', () => {
    render(<Alert type="info" title="Info" />);
    const alert = screen.getByText('Info').closest('div');
    expect(alert?.parentElement).toHaveClass('bg-blue-50');
  });

  it('renders success type', () => {
    render(<Alert type="success" title="Success" />);
    const alert = screen.getByText('Success').closest('div');
    expect(alert?.parentElement).toHaveClass('bg-green-50');
  });

  it('renders warning type', () => {
    render(<Alert type="warning" title="Warning" />);
    const alert = screen.getByText('Warning').closest('div');
    expect(alert?.parentElement).toHaveClass('bg-yellow-50');
  });

  it('renders error type', () => {
    render(<Alert type="error" title="Error" />);
    const alert = screen.getByText('Error').closest('div');
    expect(alert?.parentElement).toHaveClass('bg-red-50');
  });
});
