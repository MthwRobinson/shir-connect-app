// Renders the component for the Events screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import FileDownload from 'js-file-download';

import './Events.css';

class Events extends Component {
    downloadCSV = () => {
      // Downloads the events information csv
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token)
      axios.get('/service/export/event_aggregates',
        { headers: { Authorization: auth }})
        .then(res => {
          FileDownload(res.data, 'event_aggregates.csv');
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          }
        })
    }
    
    render() {
      return (
        <div className="Events">
          <h2>Welcome to Events!</h2><hr/>
          <i 
            className="fa fa-download"
            onClick={()=>this.downloadCSV()}
          ></i>
        </div>
      );
    }
}

export default withRouter(Events);
