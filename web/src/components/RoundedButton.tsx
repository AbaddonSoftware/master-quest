interface RoundedButtonProps {
  label?: string;
  href?: string;
  onClick?: () => void;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  children?: React.ReactNode;
}

export default function RoundedButton({
  label,
  href,
  onClick,
  size = "md",
  className,
  type = "button",
  disabled = false,
  children,
}: RoundedButtonProps) {
  const baseClass = ["btn-parchment", `btn-${size}`, className]
    .filter(Boolean)
    .join(" ");

  if (href) {
    return (
      <a href={href} onClick={() => onClick?.()} className={baseClass}>
        {children ?? label}
      </a>
    );
  }

  return (
    <button type={type} onClick={onClick} className={baseClass} disabled={disabled}>
      {children ?? label}
    </button>
  );
}
