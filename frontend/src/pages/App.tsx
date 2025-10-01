import { useState } from "react";

import { Site } from "../lib/api";
import { SiteDetails } from "../components/SiteDetails";
import { SiteForm } from "../components/SiteForm";
import { SiteList } from "../components/SiteList";

export default function App() {
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);

  return (
    <div className="container">
      <h1>Générateur d'annuaires métiers</h1>
      <p>
        Configurez vos annuaires métiers, importez les données SIRENE, géocodez les établissements et
        gérez vos pages personnalisées.
      </p>
      <div className="flex">
        <div style={{ flex: 1 }}>
          <SiteForm onCreated={setSelectedSite} />
          <SiteList onSelect={setSelectedSite} selectedSiteId={selectedSite?.id} />
        </div>
        <div style={{ flex: 2 }}>
          {selectedSite ? (
            <SiteDetails site={selectedSite} />
          ) : (
            <div className="card">
              <p>Sélectionnez un site pour afficher ses détails.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
