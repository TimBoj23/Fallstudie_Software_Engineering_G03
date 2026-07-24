import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { getAssets } from "../api/assetsApi.js";
import Button from "../components/Button.jsx";
import DateTimeRangeFields from "../components/DateTimeRangeFields.jsx";
import EmptyState from "../components/EmptyState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import Panel from "../components/Panel.jsx";
import ResourceCard from "../components/ResourceCard.jsx";
import StatusMessage from "../components/StatusMessage.jsx";

const assetTypes = ["", "beamer", "whiteboard", "laptop", "monitor", "adapter", "moderation", "presentation_tech", "other"];
const assetTypeLabels = {
  beamer: "Beamer",
  whiteboard: "Whiteboard",
  laptop: "Laptop",
  monitor: "Monitor",
  adapter: "Adapter",
  moderation: "Moderation",
  presentation_tech: "Präsentationstechnik",
  other: "Sonstiges",
};

export default function Assets({ openCreateBooking }) {
  const [filters, setFilters] = useState({ q: "", type: "", start: "", end: "" });
  const [state, setState] = useState({ loading: true, error: "", assets: [] });

  async function load(params = filters) {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const data = await getAssets(withAvailabilityMode(params));
      setState({ loading: false, error: "", assets: data.assets || [] });
    } catch (error) {
      setState({ loading: false, error: error.message, assets: [] });
    }
  }

  useEffect(() => {
    load();
  }, []);

  function submit(event) {
    event.preventDefault();
    load(filters);
  }

  return (
    <div className="page-stack">
      <Panel title="Ausstattung" caption="Beamer, Laptops, Monitore und weitere Ressourcen finden.">
        <form className="filter-bar" onSubmit={submit}>
          <input placeholder="Suchbegriff" value={filters.q} onChange={(event) => setFilters({ ...filters, q: event.target.value })} />
          <select value={filters.type} onChange={(event) => setFilters({ ...filters, type: event.target.value })}>
            {assetTypes.map((type) => <option key={type || "all"} value={type}>{assetTypeLabels[type] || "Alle Typen"}</option>)}
          </select>
          <DateTimeRangeFields values={filters} onChange={setFilters} />
          <Button type="submit" icon={Search}>Suchen</Button>
        </form>
      </Panel>

      {state.error && <StatusMessage type="danger">{state.error}</StatusMessage>}
      {state.loading ? <LoadingState /> : (
        <div className="resource-grid">
          {state.assets.length === 0 ? (
            <EmptyState title="Keine Ausstattung gefunden" text="Passe Filter oder Zeitraum an." />
          ) : state.assets.map((asset) => (
            <ResourceCard
              key={asset.id}
              title={asset.name}
              meta={assetTypeLabels[asset.asset_type] || "Ausstattung"}
              location={asset.location}
              description={asset.description}
              chips={[assetTypeLabels[asset.asset_type]].filter(Boolean)}
              imageUrl={asset.image_url}
              available={asset.available}
              onBook={() => openCreateBooking({ targetType: "asset", targetId: asset.id })}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function withAvailabilityMode(params) {
  return params.start && params.end ? { ...params, availability: "all" } : params;
}
