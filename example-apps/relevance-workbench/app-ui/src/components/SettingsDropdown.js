import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";
import { Cog6ToothIcon } from "@heroicons/react/24/outline";

import SettingsOption from "./SettingsOption";

export default function SettingsDropdown({ globalSettings, setGlobalSettings }) {

  const handleshowMetadata = () => {
    setGlobalSettings({
      ...globalSettings,
      showMetadata: !globalSettings.showMetadata,
    });
  };

  const handleCompareResults = () => {
    setGlobalSettings({
      ...globalSettings,
      compareResults: !globalSettings.compareResults,
    });
  };

  return (
    <Menu 
      as="div" 
      className="relative inline-block text-left ml-auto"
    >
      <div>
        <Menu.Button className="flex items-center rounded-full bg-transparent opacity-50 text-white hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100">
          <span className="sr-only">Open options</span>
          <Cog6ToothIcon className="h-6 w-6" aria-hidden="true" />
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="py-1">
            <Menu.Item>
              <div className="cursor-pointer flex items-center px-4 py-2 text-sm text-gray-700" onClick={handleshowMetadata}>
                <SettingsOption enabled={globalSettings.showMetadata} />
                <span className="ml-2">Show result metadata</span>
              </div>
            </Menu.Item>
            <Menu.Item>
              <div className="flex items-center px-4 py-2 text-sm text-gray-700" onClick={handleCompareResults}>
                <SettingsOption enabled={globalSettings.compareResults} />
                <span className="ml-2">Compare results</span>
              </div>
            </Menu.Item>
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
