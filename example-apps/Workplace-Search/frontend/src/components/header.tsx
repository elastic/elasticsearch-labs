// eslint-disable-next-line 
// @ts-ignore
import elasticTypeMark from "./images/elasticTypeMark.png";
import {
  thunkActions,
  useAppDispatch,
  useAppSelector,
} from "../store/provider";
export const Header = () => {
  const dispatch = useAppDispatch();
  const userRole = useAppSelector((state) => state.userRole);

  return (
    <div className="flex flex-row justify-between space-x-6 px-8 py-3.5 bg-dark-ink w-full">
      <div className="pr-8 border-r border-ink">
        <img width={118} height={40} src={elasticTypeMark} />
      </div>
      <div className="flex self-end">
        <select
          onChange={(e) => {
            dispatch(
              thunkActions.setUserRole(e.target.value as "demo" | "manager")
            );
          }}
          value={userRole}
          className="bg-dark-ink text-light-fog font-medium flex-row items-center justify-center w-36 px-4 py-2 rounded-md focus:outline-none"
        >
          <option value="demo">Engineer</option>
          <option value="manager">Manager</option>
        </select>
      </div>
    </div>
  );
};
