// Renders the component for the Events screen
import React, { Component } from 'react';
import {
  Button,
  Form,
  FormControl,
  FormGroup,
  Row,
  Table
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import moment from 'moment';
import FileDownload from 'js-file-download';

import Loading from './../Loading/Loading';

import './Events.css';

const LIMIT = 25

class Events extends Component {
    state = {
      events: [],
      pages: 1,
      page: 1,
      count: 0,
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
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token)
      const url = '/service/events?limit='+LIMIT+'&page='+this.state.page
      axios.get(url, { headers: { Authorization: auth }})
        .then(res => {
          let events = [];
          for(var i=0; i<res.data.results.length; i++){
            let event = res.data.results[i];
            var start = moment(event.start_datetime);
            event.start = start.format('MM/DD/YY, h:mm a');
            var end = moment(event.end_datetime);
            events.push(event);
          }

          this.setState({
            events: events,
            count: parseInt(res.data.count),
            pages: parseInt(res.data.pages),
            loading: false
          });
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          }
        })
    }

    incrementPage = (direction) => {
      // Increments the page number
      if (direction==='up'){
        if(this.state.page<this.state.pages){
          const page = this.state.page + 1;
          this.setState({page:page});
        }
      } else if(direction==='down') {
        if(this.state.page>1){
          const page = this.state.page - 1;
          this.setState({page:page});
        }
      }
      this.getEvents();
    }

    renderPageCount = () => {
      // Renders the page count at the top of the table
      let leftCaret = null
      if (this.state.page>1){
        leftCaret = (
          <i 
            className='fa fa-caret-left paging-arrows'
            onClick={()=>this.incrementPage('down')}
          >
          </i>
        );
      }
      let rightCaret = null
      if (this.state.page<this.state.pages){
        rightCaret = (
          <i 
            className='fa fa-caret-right paging-arrows'
            onClick={()=>this.incrementPage('up')}
          >
          </i>
        );
      }

      return(
        <div className='paging pull-left'>
            {leftCaret}
            {this.state.page}/{this.state.pages}
            {rightCaret}
        </div>
      )
    }

    renderTable = () => {
      // Creates the table with event information
      return(
        <div>
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>Event</th>
                  <th className='table-heading'>
                    Start
                    <i className='fa fa-caret-down paging-arrows'></i>
                  </th>
                  <th className='table-heading'>End</th>
                  <th className='table-heading'>Fees</th>
                  <th className='table-heading'>Attendees</th>
                </tr>
              </thead>
              <tbody>
                {this.state.events.map((event, index) => {
                  return(
                    <tr className='table-row' key={index}>
                      <th>{event.name}</th>
                      <th>{event.start}</th>
                      <th>{event.end}</th>
                      <th>${event.total_fees != null ? event.total_fees.toFixed(2) : 0.00}</th>
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

      let pageCount = this.renderPageCount();

      return (
        <div className="Events">
          <div className='events-header'>
            <h2>
              Events ({this.state.count})
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
          <div className='event-header'>
            {pageCount}
            <div className='pull-right'>
              <Form inline>
                <FormGroup>
                  <FormControl type="text" />
                </FormGroup>
                <Button className='search-button'>Search</Button>
              </Form>
            </div>
          </div>
            {table}
        </div>
      );
    }
}

export default withRouter(Events);
