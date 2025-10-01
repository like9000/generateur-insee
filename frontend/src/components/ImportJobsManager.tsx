import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ImportJob, api } from "../lib/api";

interface Props {
  siteId: number;
}

export function ImportJobsManager({ siteId }: Props) {
  const queryClient = useQueryClient();
  const { data: jobs } = useQuery({
    queryKey: ["imports", siteId],
    queryFn: async () => {
      const { data } = await api.get<ImportJob[]>(`/sites/${siteId}/imports`);
      return data;
    },
    refetchInterval: 3000
  });

  const [naf, setNaf] = useState("");
  const [department, setDepartment] = useState("");
  const [city, setCity] = useState("");

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        naf_code: naf || undefined,
        department: department || undefined,
        city: city || undefined
      };
      const { data } = await api.post<ImportJob>(`/sites/${siteId}/imports`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["imports", siteId] });
      setNaf("");
      setDepartment("");
      setCity("");
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <div className="card">
      <h2>Import SIRENE</h2>
      <form onSubmit={handleSubmit} className="flex-column">
        <label>Code NAF</label>
        <input value={naf} onChange={(e) => setNaf(e.target.value)} placeholder="ex: 4332A" />
        <label>Département</label>
        <input value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="ex: 75" />
        <label>Code Commune</label>
        <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="ex: 75101" />
        <button className="btn-primary" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Import en cours..." : "Lancer l'import"}
        </button>
      </form>
      <div className="flex-column" style={{ marginTop: "1.5rem" }}>
        {jobs?.map((job) => (
          <div key={job.id}>
            <h3>Import #{job.id}</h3>
            <p>Statut : {job.status}</p>
            <p>Entreprises importées : {job.total_imported}</p>
            <p>Etablissements fermés : {job.total_closed}</p>
            {job.last_error && <p>Erreur : {job.last_error}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
