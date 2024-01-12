import { SearchApplicationSettings } from "../components/SearchApplicationSettings";

export function SettingsPage() {
  return (
    <div className="flex justify-center min-h-screen">
      <div className="w-full max-w-2xl">
        <SearchApplicationSettings />
      </div>
    </div>
  );
}
