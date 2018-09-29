// Renders the component for the Events screen
import React, { Component } from 'react';
import { 
  Col, 
  Row,
  Table
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import moment from 'moment';
import FileDownload from 'js-file-download';

import './Events.css';

class Events extends Component {
    state = {
      events: []
    }
  
    componentDidMount(){
      this.getEvents();
    }

    downloadCSV = () => {
      // Downloads the events information csv
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
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

    getEvents = () => {
      // Pulls events to display in a table
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token)
      axios.get('/service/events?limit=25',
        { headers: { Authorization: auth }})
        .then(res => {
          this.setState({events: res.data});
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          }
        })

    }

    renderTable = () => {
      // Creates the table with event information
      return(
        <div>
          <Table responsive header hover>
            <thead>
              <tr>
                <th>Event</th>
                <th>Start</th>
                <th>End</th>
                <th>Zip Code</th>
                <th>Total Fees</th>
                <th>Attendees</th>
              </tr>
            </thead>
            <tbody>
              {this.state.events.map((event, index) => {
                return(
                  <tr className='table-row' key={index}>
                    <th>{event.name}</th>
                    <th>{event.start_datetime}</th>
                    <th>{event.end_datetime}</th>
                    <th>{event.postal_code}</th>
                    <th>{event.total_fees}</th>
                    <th>{event.attendee_count}</th>
                  </tr>
                )
              })}
            </tbody>
          </Table>
        </div>
      )

    }

    
   render() {
      let table = this.renderTable();

      return (
        <div className="Events">
          <div className='events-header'>
            <h2>
              Upcoming Events
              <i 
                className="fa fa-times pull-right event-icons"
                onClick={()=>this.props.history.push('/')}
              >
              </i>
              <i 
                className="fa fa-download pull-right event-icons"
                onClick={()=>this.downloadCSV()}
              ></i>
            </h2><hr/>
          </div>
          <Row className='event-table'>
            {table}
          </Row>
        </div>
      );
    }
}

export default withRouter(Events);
