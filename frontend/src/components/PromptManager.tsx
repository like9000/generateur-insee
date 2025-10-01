import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { GenerationResponse, PromptTemplate, api } from "../lib/api";

interface Props {
  siteId: number;
}

export function PromptManager({ siteId }: Props) {
  const queryClient = useQueryClient();
  const { data: prompts } = useQuery({
    queryKey: ["prompts", siteId],
    queryFn: async () => {
      const { data } = await api.get<PromptTemplate[]>(`/sites/${siteId}/prompts`);
      return data;
    }
  });

  const [label, setLabel] = useState("");
  const [prompt, setPrompt] = useState("");
  const [scope, setScope] = useState("city");
  const [selectedPrompt, setSelectedPrompt] = useState<number | undefined>();
  const [variables, setVariables] = useState("{\"ville\": \"Paris\"}");
  const [result, setResult] = useState<GenerationResponse | null>(null);

  const createMutation = useMutation({
    mutationFn: async () => {
      const payload = { label, prompt, scope };
      const { data } = await api.post<PromptTemplate>(`/sites/${siteId}/prompts`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prompts", siteId] });
      setLabel("");
      setPrompt("");
      setScope("city");
    }
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      if (!selectedPrompt) {
        throw new Error("Sélectionnez un prompt");
      }
      let variablesObject: Record<string, string>;
      try {
        variablesObject = JSON.parse(variables);
      } catch (error) {
        throw new Error("Variables JSON invalides");
      }
      const { data } = await api.post<GenerationResponse>(`/sites/${siteId}/generate`, {
        template_id: selectedPrompt,
        variables: variablesObject
      });
      return data;
    },
    onSuccess: (data) => {
      setResult(data);
    }
  });

  const handleCreate = (event: FormEvent) => {
    event.preventDefault();
    createMutation.mutate();
  };

  const handleGenerate = (event: FormEvent) => {
    event.preventDefault();
    generateMutation.mutate();
  };

  return (
    <div className="card">
      <h2>Prompts OpenAI</h2>
      <form onSubmit={handleCreate} className="flex-column">
        <label>Libellé</label>
        <input value={label} onChange={(e) => setLabel(e.target.value)} required />
        <label>Scope</label>
        <select value={scope} onChange={(e) => setScope(e.target.value)}>
          <option value="city">Ville</option>
          <option value="postal_code">Code postal</option>
          <option value="custom">Personnalisé</option>
        </select>
        <label>Prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          placeholder="Ex: Rédige une introduction pour {ville}"
          required
        />
        <button className="btn-primary" type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "Enregistrement..." : "Ajouter"}
        </button>
      </form>

      <div style={{ marginTop: "1.5rem" }}>
        <h3>Tester un prompt</h3>
        <form onSubmit={handleGenerate} className="flex-column">
          <label>Prompt à tester</label>
          <select
            value={selectedPrompt ?? ""}
            onChange={(e) => setSelectedPrompt(Number(e.target.value))}
            required
          >
            <option value="" disabled>
              Choisir un prompt
            </option>
            {prompts?.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
          <label>Variables (JSON)</label>
          <textarea value={variables} onChange={(e) => setVariables(e.target.value)} rows={4} />
          <button className="btn-secondary" type="submit" disabled={generateMutation.isPending}>
            {generateMutation.isPending ? "Génération..." : "Générer"}
          </button>
        </form>
        {result && (
          <div className="card" style={{ marginTop: "1rem" }}>
            <h4>Prompt envoyé</h4>
            <pre>{result.prompt}</pre>
            <h4>Contenu généré</h4>
            <p>{result.content}</p>
          </div>
        )}
      </div>
    </div>
  );
}
