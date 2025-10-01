import axios from "axios";

export const api = axios.create({
  baseURL: "/api"
});

export interface Site {
  id: number;
  name: string;
  slug: string;
  description?: string;
  sirene_filters?: Record<string, string>;
  openai_prompt?: string;
  created_at: string;
}

export interface ManualPage {
  id: number;
  site_id: number;
  title: string;
  slug: string;
  content: string;
  seo_description?: string;
  created_at: string;
  updated_at: string;
}

export interface Establishment {
  id: number;
  site_id: number;
  siren: string;
  nic: string;
  siret: string;
  business_name?: string;
  naf_code?: string;
  naf_label?: string;
  address?: string;
  postal_code?: string;
  city?: string;
  department?: string;
  is_active: boolean;
  closure_label?: string;
  geo_lat?: number;
  geo_lon?: number;
  geo_status?: string;
}

export interface ImportJob {
  id: number;
  site_id: number;
  naf_code?: string;
  department?: string;
  city?: string;
  status: string;
  created_at: string;
  updated_at: string;
  cursor?: string;
  total_imported: number;
  total_closed: number;
  total_errors: number;
  last_error?: string;
}

export interface PromptTemplate {
  id: number;
  site_id: number;
  label: string;
  prompt: string;
  scope: string;
  created_at: string;
}

export interface GenerationResponse {
  prompt: string;
  content: string;
}
