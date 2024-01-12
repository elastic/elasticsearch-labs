import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDown, faAngleUp } from "@fortawesome/free-solid-svg-icons";
import { useDispatch, useSelector } from "react-redux";
import { setFilterValue } from "../store/slices/filterSlice";
import { RootState } from "../store/store";

interface FilterProps {
  label: string;
}

export const Filter: React.FC<FilterProps> = ({ label }) => {
  const [isOpen, setIsOpen] = useState(false);

  const dispatch = useDispatch();
  const filter = useSelector((state: RootState) => state.filter["filters"])[
    label
  ];
  const { values, options } = filter;

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleCheckboxChange = (option: string) => {
    const values = filter.values;
    const newValues = values.includes(option)
      ? values.filter((v) => v !== option)
      : [...values, option];
    dispatch(setFilterValue({ label, values: newValues }));
  };

  return (
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className="flex items-center space-x-2 p-2 bg-white rounded border border-gray-300 focus:outline-none focus:border-blue-500"
      >
        <span className="font-semibold">{label}:</span>
        <span>{values.length}</span>
        {isOpen ? (
          <FontAwesomeIcon icon={faAngleUp} />
        ) : (
          <FontAwesomeIcon icon={faAngleDown} />
        )}
      </button>
      {isOpen && (
        <div className="absolute z-10 mt-2 w-64 border rounded-md shadow-lg bg-white">
          {options.map((option, index) => (
            <label
              key={index}
              className="block text-left p-2 hover:bg-gray-100 cursor-pointer"
            >
              <input
                type="checkbox"
                className="mr-2"
                value={option}
                checked={values.includes(option)}
                onChange={() => handleCheckboxChange(option)}
              />
              {option}
            </label>
          ))}
        </div>
      )}
    </div>
  );
};
