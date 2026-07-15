export default function Panel({ title, caption, actions, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      {(title || caption || actions) && (
        <div className="panel-header">
          <div>
            {title && <h2>{title}</h2>}
            {caption && <p>{caption}</p>}
          </div>
          {actions && <div className="panel-actions">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  );
}
