import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ManualPage, api } from "../lib/api";

interface Props {
  siteId: number;
}

export function ManualPagesManager({ siteId }: Props) {
  const queryClient = useQueryClient();
  const { data: pages } = useQuery({
    queryKey: ["pages", siteId],
    queryFn: async () => {
      const { data } = await api.get<ManualPage[]>(`/sites/${siteId}/pages`);
      return data;
    }
  });

  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [content, setContent] = useState("");
  const [seoDescription, setSeoDescription] = useState("");

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = { title, slug, content, seo_description: seoDescription };
      const { data } = await api.post<ManualPage>(`/sites/${siteId}/pages`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pages", siteId] });
      setTitle("");
      setSlug("");
      setContent("");
      setSeoDescription("");
    }
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <div className="card">
      <h2>Pages manuelles</h2>
      <form onSubmit={handleSubmit} className="flex-column">
        <label>Titre</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        <label>Slug</label>
        <input value={slug} onChange={(e) => setSlug(e.target.value)} required />
        <label>Contenu</label>
        <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={6} required />
        <label>Description SEO</label>
        <textarea value={seoDescription} onChange={(e) => setSeoDescription(e.target.value)} rows={3} />
        <button className="btn-primary" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Enregistrement..." : "Ajouter"}
        </button>
      </form>
      <div className="flex-column" style={{ marginTop: "1.5rem" }}>
        {pages?.map((page) => (
          <div key={page.id}>
            <h3>{page.title}</h3>
            <p>{page.seo_description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
