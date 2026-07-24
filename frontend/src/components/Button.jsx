export default function Button({
  children,
  icon: Icon,
  variant = "primary",
  size = "md",
  type = "button",
  className = "",
  ...props
}) {
  return (
    <button type={type} className={`button button-${variant} button-${size} ${className}`} {...props}>
      {Icon && <Icon size={16} />}
      {children && <span>{children}</span>}
    </button>
  );
}
