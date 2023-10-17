// store.js
import { createStore, combineReducers } from 'redux';

// Define your initial state
const initialState = {
  count: 0,
};

// Define action types
const INCREMENT = 'INCREMENT';
const DECREMENT = 'DECREMENT';

// Create action creators
export const increment = () => ({ type: INCREMENT });
export const decrement = () => ({ type: DECREMENT });

// Create a reducer
const counterReducer = (state = initialState, action) => {
  switch (action.type) {
    case INCREMENT:
      return { ...state, count: state.count + 1 };
    case DECREMENT:
      return { ...state, count: state.count - 1 };
    default:
      return state;
  }
};

// Combine multiple reducers if needed
const rootReducer = combineReducers({
  counter: counterReducer,
});

// Create the Redux store
const store = createStore(rootReducer);

export default store;
