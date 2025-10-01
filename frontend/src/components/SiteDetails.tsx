import { useQuery } from "@tanstack/react-query";

import { Site, api } from "../lib/api";
import { EstablishmentsMap } from "./EstablishmentsMap";
import { ImportJobsManager } from "./ImportJobsManager";
import { ManualPagesManager } from "./ManualPagesManager";
import { PromptManager } from "./PromptManager";

interface Props {
  site: Site;
}

export function SiteDetails({ site }: Props) {
  const { data: siteData } = useQuery({
    queryKey: ["site", site.id],
    queryFn: async () => {
      const { data } = await api.get<Site>(`/sites/${site.id}`);
      return data;
    },
    initialData: site
  });

  return (
    <div className="flex-column">
      <div className="card">
        <h1>{siteData?.name}</h1>
        <p>{siteData?.description}</p>
        <p>
          Slug : <strong>{siteData?.slug}</strong>
        </p>
      </div>
      <ImportJobsManager siteId={site.id} />
      <ManualPagesManager siteId={site.id} />
      <PromptManager siteId={site.id} />
      <EstablishmentsMap siteId={site.id} />
    </div>
  );
}
