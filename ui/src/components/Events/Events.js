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

import {
  getAccessToken,
  refreshAccessToken 
} from './../../utilities/authentication';

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
        query: '',
        searchTerms: [],
        sortColumn: 'start_datetime',
        sortOrder: 'desc'
      }

      // Bindings for search bar
      this.handleQuery = this.handleQuery.bind(this)
    }
  
    componentDidMount(){
      this.getEvents();
      refreshAccessToken();
    }

    downloadCSV = () => {
      // Downloads the events information csv
      const token = getAccessToken();
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

    getEvents = (page=1, sortCol='start_datetime', 
                 sortOrder='desc', searchTerms=[]) => {
      // Pulls events to display in a table
      this.setState({loading: true});
      const token = getAccessToken();
      const auth = 'Bearer '.concat(token)

      // Construct the URL parameters
      let url = '/service/events?limit='+LIMIT;
      url += '&page='+page
      url += '&q='+searchTerms.join(' ');
      url += '&order='+sortOrder;
      url += '&sort='+sortCol;
      
      axios.get(url, {headers: {Authorization: auth}})
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

          this.setState({
            events: events,
            count: count,
            pages: pages,
            page: page,
            loading: false,
            sortColumn: sortCol,
            sortOrder: sortOrder
          });
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          } else if(err.response.status===403){
            this.props.history.push('/forbidden');
          }
        })
    }

    incrementPage = (direction) => {
      // Increments the page number
      if (direction==='up'){
        if(this.state.page<this.state.pages){
          const page = this.state.page + 1;
          this.setState({page:page});
          this.getEvents(page, this.state.sortColumn, this.state.sortOrder,
                         this.state.searchTerms);
        }
      } else if(direction==='down') {
        if(this.state.page>1){
          const page = this.state.page - 1;
          this.setState({page:page});
          this.getEvents(page, this.state.sortColumn, this.state.sortOrder,
                         this.state.searchTerms);
        }
      }
    }

    handleSearch = (event) => {
      // Handles the submit action in the search bar
      event.preventDefault();
      let searchTerms = [...this.state.searchTerms];
      searchTerms.push(this.state.query);
      this.setState({page: 1, searchTerms: searchTerms, query: ''});
      this.getEvents(1, this.state.sortColumn, this.state.sortOrder, 
                     searchTerms);
    }

    handleSort = (sortColumn) => {
      // Changes the sort order of the columns
      let sortOrder = this.state.sortOrder;
      if(sortColumn===this.state.sortColumn){
        if(this.state.sortOrder==='asc'){
          sortOrder = 'desc';
        } else {
          sortOrder = 'asc';
        }
      }
      this.getEvents(1, sortColumn, sortOrder, this.state.searchTerms);
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
      let sortArrow = this.state.sortOrder === 'desc' ? 'down' : 'up';
      const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';
    
      return(
        <div>
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('name')}>
                    Event
                    {this.state.sortColumn === 'name'
                     ? <i className={arrowClass}></i>
                     : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('start_datetime')}>
                    Start
                    {this.state.sortColumn === 'start_datetime'
                     ? <i className={arrowClass}></i>
                     : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('venue_name')}>
                    Venue
                    {this.state.sortColumn === 'venue_name'
                     ? <i className={arrowClass}></i>
                     : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('attendee_count')}>
                    Attendees
                    {this.state.sortColumn === 'attendee_count'
                     ? <i className={arrowClass}></i>
                     : null}
                  </th>
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

      let searchTermPills = [];
      for(let searchTerm of this.state.searchTerms){
        searchTermPills.push(<div className='pull-right search-term-pill'>
          <b>{searchTerm}</b>
          <i className="fa fa-times pull-right event-icons search-term-times"></i>
        </div>)
      }

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
                <Form onSubmit={this.handleSearch} inline>
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
              {searchTermPills}
            </div>
              {table}
          </div>
        </div>
      );
    }
}

export default withRouter(Events);
