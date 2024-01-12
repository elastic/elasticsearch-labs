const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3001";

export async function callApi<T>(
  endpoint: string,
  options: RequestInit
): Promise<T> {
  const response = await fetch(API_HOST + endpoint, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });
  return await response.json();
}
