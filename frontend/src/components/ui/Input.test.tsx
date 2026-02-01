import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../../test/utils';
import Input from './Input';

describe('Input', () => {
  it('renders with placeholder', () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Input label="Username" />);
    expect(screen.getByText('Username')).toBeInTheDocument();
  });

  it('renders with helper text', () => {
    render(<Input helperText="This is helpful" />);
    expect(screen.getByText('This is helpful')).toBeInTheDocument();
  });

  it('renders with error state', () => {
    render(<Input error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveClass('border-red-300');
  });

  it('calls onChange when typing', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  it('renders left icon', () => {
    const Icon = () => <span data-testid="icon">Icon</span>;
    render(<Input leftIcon={<Icon />} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('renders right icon', () => {
    const Icon = () => <span data-testid="icon">Icon</span>;
    render(<Input rightIcon={<Icon />} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });
});
