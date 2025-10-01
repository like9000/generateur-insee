import { FormEvent, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Site, api } from "../lib/api";

interface Props {
  onCreated?: (site: Site) => void;
}

export function SiteForm({ onCreated }: Props) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [naf, setNaf] = useState("");
  const [department, setDepartment] = useState("");

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        name,
        slug,
        description,
        sirene_filters: {
          codeNaf: naf || undefined,
          codeDepartementEtablissement: department || undefined
        }
      };
      const { data } = await api.post<Site>("/sites", payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["sites"] });
      setName("");
      setSlug("");
      setDescription("");
      setNaf("");
      setDepartment("");
      onCreated?.(data);
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Créer un annuaire</h2>
      <label>Nom du site</label>
      <input value={name} onChange={(e) => setName(e.target.value)} required />
      <label>Slug</label>
      <input value={slug} onChange={(e) => setSlug(e.target.value)} required />
      <label>Description</label>
      <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
      <label>Code NAF (filtre)</label>
      <input value={naf} onChange={(e) => setNaf(e.target.value)} placeholder="ex: 4332A" />
      <label>Département</label>
      <input value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="ex: 75" />
      <button className="btn-primary" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Création..." : "Créer"}
      </button>
    </form>
  );
}
