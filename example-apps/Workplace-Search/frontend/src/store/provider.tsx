import { Result, SearchResponse } from "../types";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { ChatMessageType } from "../components/chat_message";
import { SourceType } from "../components/source_item";

import { configureStore, createSlice } from "@reduxjs/toolkit";

import { Provider, useDispatch, useSelector } from "react-redux";
import type { TypedUseSelectorHook } from "react-redux";

type GlobalStateType = {
  filters: Record<string, string[]>;
  searchResponse: SearchResponse | null;
  query: string;
  loading: boolean;
  streamMessage: string;
  conversation: ChatMessageType[];
  inProgressMessage: boolean;
  userRole: "demo" | "manager";
};

const GLOBAL_STATE: GlobalStateType = {
  filters: {},
  searchResponse: null,
  query: "",
  loading: false,
  streamMessage: "",
  conversation: [],
  inProgressMessage: false,
  userRole: "demo",
};

const API_HOST = "/api";
const defaultHeaders = {
  "Content-Type": "application/json",
};

const globalSlice = createSlice({
  name: "global",
  initialState: GLOBAL_STATE,
  reducers: {
    setStreamMessage: (state, action) => {
      state.streamMessage = action.payload.streamMessage;
    },
    addConversation: (state, action) => {
      state.conversation.push(action.payload.conversation);
    },
    setConversation: (state, action) => {
      state.conversation = [action.payload.conversation];
    },
    resetConversation: (state) => {
      state.conversation = [];
    },
    setSearchResponse: (state, action) => {
      state.searchResponse = action.payload.searchResponse;
    },
    setQuery: (state, action) => {
      state.query = action.payload.query;
    },
    setLoading: (state, action) => {
      state.loading = action.payload.loading;
    },
    setInProgressMessage: (state, action) => {
      state.inProgressMessage = action.payload.inProgressMessage;
    },
    setFilters: (state, action) => {
      state.filters = action.payload.filters;
    },
    reset: (state) => {
      state.searchResponse = null;
      state.filters = {};
      state.inProgressMessage = false;
      state.streamMessage = "";
      state.conversation = [];
    },
    setUserRole: (state, action) => {
      state.userRole = action.payload.userRole;
    },
  },
});

const store = configureStore({
  reducer: globalSlice.reducer,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export const actions = globalSlice.actions;

export const hasStartedConversation = (state: RootState) => {
  const [summary, ...conversation] = state.conversation;
  return conversation.length > 0;
};

export const isFacetSelected = (
  filters: RootState["filters"],
  facet: string,
  value: string
) => {
  return filters[facet]?.includes(value);
};

export const thunkActions = {
  setUserRole(userRole: "demo" | "manager") {
    return async function setUserRole(dispatch, getState) {
      dispatch(actions.setUserRole({ userRole }));
      if (getState().query !== "") {
        dispatch(actions.reset());
        dispatch(thunkActions.search(getState().query, {}));
      }
    };
  },
  search: (query, filters) => {
    return async function fetchSearch(dispatch, getState) {
      dispatch(actions.setLoading({ loading: true }));
      dispatch(actions.setQuery({ query }));
      dispatch(actions.setFilters({ filters }));

      dispatch(actions.setInProgressMessage({ inProgressMessage: true }));
      dispatch(actions.setStreamMessage({ streamMessage: "..." }));

      const response = await fetch(`${API_HOST}/search`, {
        method: "POST",
        body: JSON.stringify({
          query: query,
          filters: filters,
          conversation_id: getState().searchResponse?.conversation_id,
          user: getState().userRole,
        }),
        headers: defaultHeaders,
      });

      const searchResponse = (await response.json()) as SearchResponse;
      dispatch(actions.setSearchResponse({ searchResponse }));
      dispatch(actions.setLoading({ loading: false }));

      let message = "";

      await fetchEventSource(`${API_HOST}/completions`, {
        method: "POST",
        openWhenHidden: true,
        body: JSON.stringify({
          streaming_id: searchResponse.streaming_id,
        }),
        headers: defaultHeaders,
        async onmessage(event) {
          if (event.data !== "[DONE]") {
            message += event.data === "" ? `${event.data} \n` : event.data;
            dispatch(actions.setStreamMessage({ streamMessage: message }));
          } else {
            const regex = /SOURCES:(.+)/;
            const sourceReferences = message.match(regex);

            let resultSourcesToAdd: Result[] = [];
            if (sourceReferences) {
              const sources = sourceReferences[1].split(",");
              resultSourcesToAdd = sources
                .map((sourceName) => {
                  return searchResponse.results.find(
                    (result) => result.name[0] === sourceName.trim()
                  );
                })
                .filter((result): result is Result => result !== undefined);
            }

            const action = hasStartedConversation(getState())
              ? actions.addConversation
              : actions.setConversation;
            dispatch(
              action({
                conversation: {
                  isHuman: false,
                  content: message.replace(regex, ""),
                  id: getState().conversation.length + 1,
                  sources: resultSourcesToAdd.map(
                    (result): SourceType => ({
                      icon: result.category[0].replace(" ", "_"),
                      name: result.name[0],
                      href: result.url[0],
                    })
                  ),
                },
              })
            );

            dispatch(actions.setStreamMessage({ streamMessage: null }));

            dispatch(
              actions.setInProgressMessage({ inProgressMessage: false })
            );
          }
        },
      });
    };
  },
  askQuestion: (query) => {
    return async function askQuestion(dispatch, getState) {
      const state = getState();
      dispatch(
        actions.addConversation({
          conversation: {
            isHuman: true,
            content: query,
            id: state.conversation.length + 1,
          },
        })
      );
      dispatch(thunkActions.search(query, state.filters));
    };
  },
  toggleFilter: (filter: string, value: string) => {
    return async function toggleFilter(dispatch, getState) {
      const state = getState();
      let stateFilters = {
        category: [...(state.filters.category || [])],
      };
      if (!stateFilters[filter]) {
        stateFilters[filter] = [];
      }
      const filterExists = state.filters[filter]?.includes(value);
      const filterValues = filterExists
        ? stateFilters[filter].filter((f) => f === filter)
        : stateFilters[filter].concat(value);

      stateFilters = {
        ...stateFilters,
        [filter]: filterValues,
      };

      if (hasStartedConversation(state)) {
        // add a message to the conversation that we are adding/removing a filter
        dispatch(
          actions.addConversation({
            conversation: {
              isHuman: true,
              content: filterExists
                ? `Please exclude sources from ${value}`
                : `Please include sources from ${value}`,
              id: state.conversation.length + 1,
            },
          })
        );
      }

      dispatch(actions.setFilters({ filters: stateFilters }));
      dispatch(thunkActions.search(state.query, stateFilters));
    };
  },
};

export const GlobalStateProvider = ({ children }) => {
  return <Provider store={store}>{children}</Provider>;
};
