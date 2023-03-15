import { configureStore, combineReducers, getDefaultMiddleware } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

import filesReducer from './slices/filesSlice';
import graphOptionsReducer from './slices/graphOptionsSlice';
import graphHtmlReducer from './slices/graphHtmlSlice';

const persistConfig = {
  key: 'root',
  storage,
};

const rootReducer = combineReducers({
  files: filesReducer,
  graphOptions: graphOptionsReducer,
  graphHtml: graphHtmlReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware({
    serializableCheck: {
      ignoredActions: ['persist/PERSIST'],
    },
  }),
});

const persistor = persistStore(store);

export { store, persistor };
