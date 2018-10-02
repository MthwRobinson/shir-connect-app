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

import Loading from './../Loading/Loading';

import './Events.css';

class Events extends Component {
    state = {
      events: [],
      loading: true
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
          let events = [];
          for(var i=0; i<res.data.length; i++){
            let event = res.data[i];
            var start = moment(event.start_datetime);
            event.start = start.format('MM/DD/YY, h:mm a');
            var end = moment(event.end_datetime);
            event.end = end.format('MM/DD/YY, h:mm a');
            events.push(event);
          }

          this.setState({
            events: events,
            loading: false
          });
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
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th>Event</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Zip</th>
                  <th>Fees</th>
                  <th>Attendees</th>
                </tr>
              </thead>
              <tbody>
                {this.state.events.map((event, index) => {
                  return(
                    <tr className='table-row' key={index}>
                      <th>{event.name}</th>
                      <th>{event.start}</th>
                      <th>{event.end}</th>
                      <th>{event.postal_code}</th>
                      <th>${event.total_fees.toFixed(2)}</th>
                      <th>{event.attendee_count}</th>
                    </tr>
                  )
                })}
              </tbody>
            </Table>
          </Row>
        </div>
      )

    }

    render() {
      let table = null
      if(this.state.loading){
        table = (
          <div className='event-loading'>
            <Loading/>
          </div>
        );
      } else {
        table = this.renderTable();
      }

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
            {table}
        </div>
      );
    }
}

export default withRouter(Events);
