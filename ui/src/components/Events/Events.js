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
import ReactToolTip from 'react-tooltip';
import axios from 'axios';
import moment from 'moment';
import FileDownload from 'js-file-download';

import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Events.css';

const LIMIT = 25

class Events extends Component {
    constructor(props){
      super(props);
      this.state = {
        events: [],
        pages: 1,
        page: 1,
        count: 0,
        loading: true,
        query: ''
      }

      // Bindings for search bar
      this.handleQuery = this.handleQuery.bind(this)
    }
  
    componentDidMount(){
      this.getEvents('initial');
    }

    downloadCSV = () => {
      // Downloads the events information csv
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
      let url = '/service/events/export';
      if(this.state.query.trim().length>0){
        url += '?q='+this.state.query;
      }
      axios.get(url, {headers: {Authorization: auth}})
        .then(res => {
          let filename = 'trs_events';
          if(this.state.query.trim().length>0){
             filename += '_'+this.state.query;
          }
          const today = moment().format('YYYYMMDD');
          filename += '_'+ today + '.csv';
          FileDownload(res.data, filename);
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          }
        })
    }

    getEvents = (fetchType) => {
      // Pulls events to display in a table
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token)
      let url = '/service/events?limit='+LIMIT;

      // Load settings from session storage
      const eventPage = sessionStorage.getItem('eventPage');
      const eventPages = sessionStorage.getItem('eventPages');
      const eventQuery = sessionStorage.getItem('eventQuery');
      const eventCount = sessionStorage.getItem('eventCount');
      let settingsLoaded = false
      if(eventPage&&eventPages&&eventCount){
        settingsLoaded = true
      }

      // Determine the correct page to load
      if(fetchType==='search'){
        url += '&page=1';
      } else if(fetchType==='up'){
        url += '&page='+(this.state.page+1); 
      } else if(fetchType==='down') {
        url += '&page='+(this.state.page-1); 
      } else if(fetchType==='initial'&&settingsLoaded){
        url += '&page='+eventPage;
        this.setState({ 
          page: parseInt(eventPage, 10),
          pages: parseInt(eventPages, 10),
          count: parseInt(eventCount, 10),
          query: eventQuery
        });
      } else {
        url += '&page='+this.state.page;
      }

      // Parse the event query
      if(fetchType==='initial'&&settingsLoaded&&eventQuery){
        if(eventQuery.trim().length>0){
          url += '&q='+eventQuery;
        }
      } else {
        if(this.state.query.trim().length>0){
          url += '&q='+this.state.query;
        }
      }
      
      axios.get(url, { headers: { Authorization: auth }})
        .then(res => {
          let events = [];
          for(var i=0; i<res.data.results.length; i++){
            let event = res.data.results[i];
            var start = moment(event.start_datetime);
            event.start = start.format('MM/DD/YY, h:mm a');
            var end = moment(event.end_datetime);
            event.end = end.format('MM/DD/YY, h:mm a');
            events.push(event);
          }
          const pages = parseInt(res.data.pages, 10);
          const count = parseInt(res.data.count, 10);

          // Save settings in session storage and update state
          sessionStorage.setItem('eventPages', pages);
          sessionStorage.setItem('eventPage', this.state.page);
          sessionStorage.setItem('eventQuery', this.state.query);
          sessionStorage.setItem('eventCount', count);

          this.setState({
            events: events,
            count: count,
            pages: pages,
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
          this.getEvents('up');
        }
      } else if(direction==='down') {
        if(this.state.page>1){
          const page = this.state.page - 1;
          this.setState({page:page});
          this.getEvents('down');
        }
      }
    }

    handleSubmit = (event) => {
      // Handles the submit action in the search bar
      event.preventDefault();
      this.setState({page: 1});
      this.getEvents('search');
    }

    handleQuery(event){
      // Updates the query value in the state
      this.setState({
        query: event.target.value
      });
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
                  <th className='table-heading'>Venue</th>
                  <th className='table-heading'>Attendees</th>
                </tr>
              </thead>
              <tbody>
                {this.state.events.map((event, index) => {
                  return(
                    <tr 
                      className='table-row' 
                      key={index}
                      onClick={()=> 
                        this.props.history.push('/event?id='+event.id)}
                    >
                      <th>{event.name}</th>
                      <th>{event.start}</th>
                      <th>{event.venue_name !== null 
                          ? event.venue_name : 'Temple Rodef Shalom'}</th>
                      <th>{event.attendee_count != null 
                          ? event.attendee_count : 0}</th>
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
        <div>
          <Header />
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
                <Form onSubmit={this.handleSubmit} inline>
                  <FormGroup>
                    <FormControl 
                      value={this.state.query}
                      onChange={this.handleQuery}
                      type="text" 
                    />
                  </FormGroup>
                  <Button 
                    className='search-button'
                    type="submit"
                    data-tip="Returns searchs fesults for the event name."
                  >Search</Button>
                </Form>
                <ReactToolTip />
              </div>
            </div>
              {table}
          </div>
        </div>
      );
    }
}

export default withRouter(Events);
