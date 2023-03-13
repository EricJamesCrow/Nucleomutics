import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import store from './redux/store'

import App from './App';

// chakra ui components
import { ChakraProvider } from '@chakra-ui/react'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ChakraProvider>
            <Provider store={store}>
                <App/>
            </Provider>
        </ChakraProvider>
    </React.StrictMode>
);