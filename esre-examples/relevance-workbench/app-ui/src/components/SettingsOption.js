import { Switch } from "@headlessui/react";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function SettingsOption({ enabled }) {

  return (
    <Switch
      checked={enabled}
      className="pointer-events-none group relative inline-flex h-4 w-6 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      <span className="sr-only">Use setting</span>
      <span
        aria-hidden="true"
        className="pointer-events-none absolute h-full w-full rounded-md bg-white"
      />
      <span
        aria-hidden="true"
        className={classNames(
          enabled ? "bg-elastic-blue-light" : "bg-gray-200",
          "pointer-events-none absolute mx-auto h-3 w-5 rounded-full transition-colors duration-200 ease-in-out"
        )}
      />
      <span
        aria-hidden="true"
        className={classNames(
          enabled ? "translate-x-3" : "translate-x-0",
          "pointer-events-none absolute left-0 inline-block h-3 w-3 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out"
        )}
      />
    </Switch>
  );
}
