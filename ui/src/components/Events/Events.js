// Renders the component for the Events screen
import React, { Component } from 'react';
import {
  Button,
  Form,
  FormControl,
  FormGroup,
  Label,
  Row,
  Table
} from 'react-bootstrap';
import DatePicker from 'react-datepicker';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import moment from 'moment';
import FileDownload from 'js-file-download';
import ReactTooltip from 'react-tooltip';
import Modal from 'react-responsive-modal';
import Swipe from 'react-easy-swipe';

import { refreshAccessToken } from './../../utilities/authentication';
import { getDefaultLocation } from './../../utilities/map';

import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Events.css';
import "react-datepicker/dist/react-datepicker.css";

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
        sortOrder: 'desc',
        defaultEventLocation: null,
        startDate: null,
        endDate: new Date(),
        showFilter: false
      }

      // Bindings for search bar
      this.handleQuery = this.handleQuery.bind(this)
      this.handleStartDate = this.handleStartDate.bind(this)
      this.handleEndDate = this.handleEndDate.bind(this)
    }

    componentDidMount(){
      getDefaultLocation()
        .then(res => {
          this.setState({defaultEventLocation: res.data.name});
          this.getEvents();
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          } else {
            this.props.history.push('/server-error');
          }
        })
      refreshAccessToken();
    }

    downloadCSV = () => {
      // Downloads the events information csv
      let url = '/service/events/export';
      if(this.state.query.trim().length>0){
        url += '?q='+this.state.query;
      }
      axios.get(url)
        .then(res => {
          let filename = 'trs_events';
          if(this.state.query.trim().length>0){
             filename += '_'+this.state.query;
          }
          const today = moment().format('YYYYMMDD');
          filename += '_'+ today + '.csv';
          FileDownload(res.data, filename);
        })
    }

    getEvents = (page=1, sortCol='start_datetime',
                 sortOrder='desc', searchTerms=[]) => {
      // Pulls events to display in a table
      // Params
      // ------
      //   page: int
      //   sortCol: the column to sort on. must
      //     be a valid column in the events table
      //   sortOrder: the order of sort. must be asc or desc
      //   searchTerm: an array of search terms to apply. all search
      //   terms are applied as an AND condition
      this.setState({loading: true});
      // Construct the URL parameters
      let url = '/service/events?limit='+LIMIT;
      url += '&page='+page
      url += '&q='+searchTerms.join(' ');
      url += '&order='+sortOrder;
      url += '&sort='+sortCol;
      if(sessionStorage.getItem('demoMode')==='true'){
        url += '&fake_data=true'
      }
      if(this.state.startDate){
        const filterStart = moment(this.state.startDate).format('YYYY-MM-DD')
        url += '&start_date='+filterStart;
      }
      if(this.state.endDate){
        const filterEnd = moment(this.state.endDate).format('YYYY-MM-DD')
        url += '&end_date='+filterEnd;
      }

      axios.get(url)
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
          } else {
            this.props.history.push('/server-error');
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

    handleFilter = (event) => {
      // Handles filtering
      event.preventDefault();
      this.getEvents(1, this.state.sortColumn, this.state.sortOrder,
                     this.state.searchTerms);
      this.hideFilter();
    }

    clearFilter = () => {
      // Clears the filter settings
      this.setState({
        showFilter: false,
        startDate: null,
        endDate: new Date(),
      })
      this.getEvents(1, this.state.sortColumn, this.state.sortOrder,
                     this.state.searchTerms);
    }

    showFilter = () => {
      this.setState({ showFilter: true })
    }

   hideFilter = () => {
      this.setState({ showFilter: false })
    }

    handleRemoveTerm = (removeTerm) => {
      // Removes search term from the search terms list
      let searchTerms = [...this.state.searchTerms];
      let updatedTerms = [];
      for(let term of searchTerms){
        if(term!==removeTerm){
          updatedTerms.push(term)
        }
      }
      this.setState({page: 1, searchTerms: updatedTerms, query: ''});
      this.getEvents(1, this.state.sortColumn, this.state.sortOrder,
                     updatedTerms);
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
      this.setState({query: event.target.value});
    }

    handleStartDate(event){
      // Updates the start date in the state
      console.log(moment(event).format('YYYY-MM-DD'));
      this.setState({startDate: event});
    }

    handleEndDate(event){
      // Updates the start date in the state
      this.setState({endDate: event});
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
            {rightCaret}{' '}
        </div>
      )
    }

    renderTable = () => {
      // Creates the table with event information
      let sortArrow = this.state.sortOrder === 'desc' ? 'down' : 'up';
      const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';

      return(
        <div>
          <Row className='table-responsive event-table'>
            <Swipe
              onSwipeRight={()=>this.incrementPage('down')}
              onSwipeLeft={()=>this.incrementPage('up')}
            >
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
                            ? event.venue_name : this.state.defaultEventLocation}</th>
                        <th>{event.attendee_count != null
                            ? event.attendee_count : 0}</th>
                      </tr>
                    )
                  })}
                </tbody>
              </Table>
            </Swipe>
          </Row>
        </div>
      )
    }

    renderFilter = () => {
      // Renders the filter options
      return(
        <Modal
          open={this.state.showFilter}
          showCloseIcon={false}
          center
        >
          <h4>Filter
            <i className='fa fa-times pull-right event-icons'
               onClick={()=>this.hideFilter()}
            ></i>
          </h4><hr/>
          <Form onSubmit={this.handleFilter} >
              <FormGroup>
                <Label className="filter-form-label">Minimum Date:</Label>
                <DatePicker
                  selected={this.state.startDate}
                  onChange={this.handleStartDate}
                  maxDate={this.state.endDate}
                  className="form-control filter-form-date-input"
                />
              </FormGroup>
              <FormGroup>
                <Label className="filter-form-label">Maximum Date:</Label>
                <DatePicker
                  selected={this.state.endDate}
                  onChange={this.handleEndDate}
                  minDate={this.state.startDate}
                  className="form-control filter-form-date-input"
                />
              </FormGroup>
              <Button
                className='search-button'
                bsStyle="primary"
                type="submit"
              >Apply Filter</Button>
              <Button
                className='search-button'
                bsStyle="danger"
                onClick={()=>this.clearFilter()}
              >Clear Filter</Button>
          </Form>
        </Modal>
      )
    }

    renderSearch = () => {
      // Renders the search bar
      return (
        <div>
          <div className='pull-right'>
            <Form onSubmit={this.handleSearch} inline>
              <FormGroup>
                <FormControl
                  className='search-box'
                  value={this.state.query}
                  onChange={this.handleQuery}
                  type="text"
                />
              </FormGroup>
              <Button
                bsStyle="primary"
                className='search-button'
                type="submit"
                data-tip="Returns searchs fesults for the event name."
              >Search</Button>
            </Form>
          </div>
        </div>
      )
    }

    renderSearchTermPills = () => {
      // Renders the pill buttons for the active search terms
      let searchTermPills = [];
      for(let searchTerm of this.state.searchTerms){
        searchTermPills.push(<div className='pull-right search-term-pill'>
          <b>{searchTerm}</b>
          <i
            className="fa fa-times pull-right event-icons search-term-times"
            onClick={()=>this.handleRemoveTerm(searchTerm)}>
          </i>
        </div>)
      }
      return searchTermPills
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
      let search = this.renderSearch();
      let filter = this.renderFilter();
      let searchTermPills = this.renderSearchTermPills();
      let info = "There are " + String(this.state.count) + " total events. <br/>";
      info += "Click or tap on an event for more information. <br/>";
      info += "On tablet, swipe right or left to switch pages.";
      return (
        <div>
          <Header />
          <div className="Events">
            <div className='events-header'>
              <h2>
                Events{' '}
                <sup><i className='fa fa-info-circle'
                        data-tip={info}></i>
                </sup>
                <i
                  className="fa fa-times pull-right event-icons"
                  onClick={()=>this.props.history.push('/')}
                >
                </i>
                <i className='fa fa-filter pull-right event-icons'
                   data-tip="Add a filter to the table."
                   onClick={()=>this.showFilter()}>
                </i>
                <i
                  className="fa fa-download pull-right event-icons"
                  data-tip="Download the table of participants"
                  onClick={()=>this.downloadCSV()}
                ></i>
              </h2><hr/>
            </div>
            <div className='event-header'>
              {pageCount}
              {search}
            </div>
            <div className='search-term-row pull-right'>
              {searchTermPills.length > 0
                ? <span id='search-term-list'><b>Search Terms:</b></span>
                : null}
              {searchTermPills}
            </div>
            {filter}
            {table}
          </div>
          <ReactTooltip html={true} />
        </div>
      );
    }
}

export default withRouter(Events);
