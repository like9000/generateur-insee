import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { useQuery } from "@tanstack/react-query";

import { Establishment, api } from "../lib/api";

interface Props {
  siteId: number;
}

export function EstablishmentsMap({ siteId }: Props) {
  const { data: establishments } = useQuery({
    queryKey: ["establishments", siteId],
    queryFn: async () => {
      const { data } = await api.get<Establishment[]>(`/sites/${siteId}/establishments`);
      return data.filter((item) => item.geo_lat && item.geo_lon);
    },
    refetchInterval: 5000
  });

  const center = establishments?.length
    ? [establishments[0].geo_lat!, establishments[0].geo_lon!] as [number, number]
    : [48.8566, 2.3522];

  return (
    <div className="card">
      <h2>Carte des établissements</h2>
      <MapContainer center={center} zoom={6} style={{ height: "400px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {establishments?.map((establishment) => (
          <Marker key={establishment.id} position={[establishment.geo_lat!, establishment.geo_lon!]}>
            <Popup>
              <strong>{establishment.business_name || establishment.siret}</strong>
              <br />
              {establishment.address}
              <br />
              {establishment.postal_code} {establishment.city}
              <br />
              {establishment.is_active ? "Actif" : establishment.closure_label}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
