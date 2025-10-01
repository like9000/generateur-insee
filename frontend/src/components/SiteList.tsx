import { useQuery } from "@tanstack/react-query";

import { Site, api } from "../lib/api";

interface Props {
  onSelect: (site: Site) => void;
  selectedSiteId?: number;
}

export function SiteList({ onSelect, selectedSiteId }: Props) {
  const { data: sites } = useQuery({
    queryKey: ["sites"],
    queryFn: async () => {
      const { data } = await api.get<Site[]>("/sites");
      return data;
    }
  });

  return (
    <div className="card">
      <h2>Annuaires existants</h2>
      <div className="flex-column">
        {sites?.map((site) => (
          <button
            key={site.id}
            className={site.id === selectedSiteId ? "btn-primary" : "btn-secondary"}
            onClick={() => onSelect(site)}
          >
            {site.name}
          </button>
        ))}
        {(!sites || sites.length === 0) && <p>Aucun site pour le moment.</p>}
      </div>
    </div>
  );
}
