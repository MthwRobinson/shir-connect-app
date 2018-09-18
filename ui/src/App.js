import React, { Component } from 'react';

import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/font-awesome/css/font-awesome.min.css';
import 'react-sliding-pane/dist/react-sliding-pane.css';

import Header from './components/Header/Header';

class App extends Component {
  render() {
    return (
      <div className="App">
        <Header></Header>
      </div>
    );
  }
}

export default App;
