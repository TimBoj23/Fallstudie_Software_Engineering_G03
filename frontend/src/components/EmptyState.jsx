export default function EmptyState({ title, text, action }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      {text && <p>{text}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}
