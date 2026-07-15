export default function LoadingState({ label = "Daten werden geladen..." }) {
  return (
    <div className="loading-state">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  );
}
