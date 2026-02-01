import { ExclamationTriangleIcon, XCircleIcon, CheckCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
}

export function Alert({
  type = 'info',
  title,
  children,
  dismissible = false,
  onDismiss,
}: AlertProps) {
  const styles = {
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-400',
      title: 'text-blue-800',
      text: 'text-blue-700',
    },
    success: {
      container: 'bg-green-50 border-green-200',
      icon: 'text-green-400',
      title: 'text-green-800',
      text: 'text-green-700',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-400',
      title: 'text-yellow-800',
      text: 'text-yellow-700',
    },
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-400',
      title: 'text-red-800',
      text: 'text-red-700',
    },
  };

  const icons = {
    info: InformationCircleIcon,
    success: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    error: XCircleIcon,
  };

  const Icon = icons[type];
  const style = styles[type];

  return (
    <div className={`rounded-lg border p-4 ${style.container}`}>
      <div className="flex">
        <Icon className={`h-5 w-5 flex-shrink-0 ${style.icon}`} />
        <div className="ml-3 flex-1">
          {title && <h3 className={`text-sm font-medium ${style.title}`}>{title}</h3>}
          <div className={`text-sm ${title ? 'mt-1' : ''} ${style.text}`}>{children}</div>
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className={`ml-3 inline-flex ${style.icon} hover:opacity-75`}
          >
            <XCircleIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
}
