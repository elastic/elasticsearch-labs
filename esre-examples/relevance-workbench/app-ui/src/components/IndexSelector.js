import React, {useState, useEffect, Fragment} from "react";
import classNames from "classnames";
import { Listbox, Transition } from '@headlessui/react'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid'


export default function IndexSelector({ selectedDataset, setSelectedDataset }) {

  const [availableDatasets, setAvailableDatasets] = useState()

  useEffect(() => {
    fetch(`api/datasets`)
      .then((res) => res.json())
      .then((data) => {
        if (selectedDataset === undefined) setSelectedDataset(Object.values(data)[0])
        console.log(data)
        setAvailableDatasets(data)
      });
  }, []);

  const handleDatasetChange = (dataset) => { 
    setSelectedDataset(dataset)
  }

  return (
    availableDatasets &&

    <div className="container mx-auto w-72 m-10">
      <Listbox value={selectedDataset} onChange={handleDatasetChange}>
        <div className="relative mt-1">
          <Listbox.Button className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm">
            <span className="block truncate">{selectedDataset.label}</span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon
                className="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </Listbox.Button>
          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              {Object.values(availableDatasets).map((dataset, key) => (
                <Listbox.Option
                  key={key}
                  className={({ active }) =>
                    `relative cursor-default select-none py-2 pl-10 pr-4 ${
                      active ? 'bg-amber-100 text-amber-900' : 'text-gray-900'
                    }`
                  }
                  value={dataset}
                >
                  {({ selectedDataset }) => (
                    <>
                      <span
                        className={`block truncate ${
                          selectedDataset ? 'font-medium' : 'font-normal'
                        }`}
                      >
                        {dataset.label}
                      </span>
                      {selectedDataset ? (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-amber-600">
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
    </div>
    
  );
}