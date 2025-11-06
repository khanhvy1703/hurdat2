export const apiCall = async <T>(endpoint: string): Promise<T> => {
  const res = await fetch(endpoint);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const json = await res.json();
  if (!json.success) throw new Error(json.error || "Invalid API response");

  return json.data as T;
};