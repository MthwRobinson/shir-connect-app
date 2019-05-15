// Renders the component for the Members screen
import axios from 'axios';
import moment from 'moment';
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
import { withRouter } from 'react-router-dom';
import ReactToolTip from 'react-tooltip';

import {
  getCSRFToken,
  refreshAccessToken
} from './../../utilities/authentication'; 
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Members.css';

const LIMIT = 25

class Members extends Component {
    constructor(props){
      super(props);
      this.state = {
        members: [],
        pages: 1,
        page: 1,
        count: 0,
        query: '',
        searchTerms: [],
        loading: true,
        showUpload: false,
        uploadLoading: false,
        uploadFailed: false,
        userRole: 'standard',
        minAge: null,
        maxAge: null
      }

      // Binding for the file upload in the popup
      this.uploadFile = this.uploadFile.bind(this)
      this.handleQuery = this.handleQuery.bind(this)
      this.handleMinAge = this.handleMinAge.bind(this)
      this.handleMaxAge= this.handleMaxAge.bind(this)
    }

  componentDidMount(){
      this.checkAccess(); 
      this.getMembers();
    }
  
    checkAccess = () => {
      // Checks to make sure the user has access to the 
      // member access group
      const url = '/service/member/authorize';
      axios.get(url)
        .then(res => {
          this.setState({userRole: res.data.role});
          // Refresh the token to keep the session active
          refreshAccessToken(); 

        })
        .catch(err => {
          if(err.response.status===403){
            this.props.history.push('/forbidden');
          }
        })
    }

    selectParticipant = (participantID) => {
      // Switches to the member page
      const url = '/participant?id=' + participantID;
      this.props.history.push(url);
    }

    getMembers = (page=1, sortCol='events_attended', 
                  sortOrder='desc', searchTerms=[]) => {
      // Pulls members to display in the table 
      // Params 
      // ------
      //   page: int
      //   sortCol: the column to sort on. must
      //     be a valid column in the members table
      //   sortOrder: the order of sort. must be asc or desc
      //   searchTerm: an array of search terms to apply. all search 
      //   terms are applied as an AND condition
      this.setState({loading: true});
      // Construct the URL parameters
      let url = '/service/participants?limit='+LIMIT;
      url += '&page='+page;
      url += '&q='+searchTerms.join(' ');
      url += '&sort='+sortCol;
      url += '&order='+sortOrder;
      if(this.state.minAge){
        url += '&min_age='+this.state.minAge;
      }
      if(this.state.maxAge){
        url += '&max_age='+this.state.maxAge;
      }

      axios.get(url)
        .then(res => {
          let members = [];
          for(var i=0; i<res.data.results.length; i++){
            let member = res.data.results[i];
            if(member.last_event_date){
              var last_event_date = moment(member.last_event_date);
              member.last_event_date = last_event_date.format('MM/DD/YY');
            }
            members.push(member);
          }

          const pages = parseInt(res.data.pages, 10);
          const count = parseInt(res.data.count, 10);

          this.setState({
            members: members,
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
        }
      })
    }
  
    incrementPage = (direction) => {
      // Increments the page number
      if (direction==='up'){
        if(this.state.page<this.state.pages){
          const page = this.state.page + 1;
          this.setState({page:page});
          this.getMembers(page, this.state.sortColumn, 
                          this.state.sortOrder, this.state.searchTerms);
        }
      } else if(direction==='down') {
        if(this.state.page>1){
          const page = this.state.page - 1;
          this.setState({page:page});
          this.getMembers(page, this.state.sortColumn, 
                          this.state.sortOrder, this.state.searchTerms);
        }
      }
    }

    handleSearch = (event) => {
      // Handles the submit action in the search bar
      event.preventDefault();
      let searchTerms = [...this.state.searchTerms];
      searchTerms.push(this.state.query);
      this.setState({page: 1, searchTerms: searchTerms, query: ''});
      this.getMembers(1, this.state.sortColumn, 
                      this.state.sortOrder, searchTerms);
    }

    handleFilter = (event) => {
      // Handles filtering
      event.preventDefault();
      this.getMembers(1, this.state.sortColumn, this.state.sortOrder, 
                     this.state.searchTerms);
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
      this.setState({page: 1, searchTerms: updatedTerms, query: ''})
      this.getMembers(1, this.state.sortColumn,
                     this.state.sortOrder, updatedTerms)
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
      this.getMembers(1, sortColumn, sortOrder, this.state.searchTerms);
    }

    handleQuery(event){
      // Updates the query value in the state
      this.setState({query: event.target.value});
    }
  
    handleMinAge(event){
      // Updates the min age value in the state
      this.setState({minAge: event.target.value});
    }
  
    handleMaxAge(event){
      // Updates the max age value in the state
      this.setState({maxAge: event.target.value});
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
      // Creates the table with member information
      let sortArrow = this.state.sortOrder === 'desc' ? 'down' : 'up';
      const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';

      return(
        <div>
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('first_name')}>
                    First Name
                    {this.state.sortColumn === 'first_name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('last_name')}>
                    Last Name
                    {this.state.sortColumn === 'last_name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('is_member')}>
                    Member 
                    {this.state.sortColumn === 'is_member'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('age')}>
                    Age 
                    {this.state.sortColumn === 'age'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('events_attended')}>
                    Events
                    {this.state.sortColumn === 'events_attended'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('last_event_date')}>
                    Most Recent
                    {this.state.sortColumn === 'last_event_date'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('event_name')}>
                    Event Name
                    {this.state.sortColumn === 'event_name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                </tr>
              </thead>
              <tbody>
                {this.state.members.map((member, index) => {
                  return(
                    <tr 
                      className='table-row' 
                      key={index}
                      onClick={()=>this.selectParticipant(member.participant_id)}
                    >
                      <th>{member.first_name != null
                          ? member.first_name : '--'}</th>
                      <th>{member.last_name != null
                          ? member.last_name : '--'}</th>
                      <th>{member.is_member === true
                          ? 'Y' : 'N'}</th>
                      <th>{member.age != null
                          ? member.age : null}</th>
                      <th>{member.events_attended != null
                          ? member.events_attended : 0}</th>
                      <th>{member.last_event_date != null
                          ? member.last_event_date : 'None'}</th>
                      <th>{member.event_name != null
                          ? member.event_name : 'None'}</th>
                    </tr>
                  )
                })}
              </tbody>
            </Table>
          </Row>
        </div>
      )
    }

    uploadFile(event) {
      // Handles uploading the member data in the popup
      event.preventDefault();
      this.setState({uploadLoading: true});

      // Get the file information
      const data = new FormData();
      const file = this.uploadInput.files[0];
      data.append('file', file);

      // Post the data
      const csrfToken = getCSRFToken();
      const url = '/service/members/upload';
      axios.post(url, data, {
          headers: {
            'X-CSRF-TOKEN': csrfToken,
            'Content-Type': 'application/vnd.ms-excel'
          }
      }).then(res => {
          this.getMembers();
          this.hideUpload();
          this.setState({uploadLoading: false});
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          } else {
            this.setState({
              uploadLoading: false,
              uploadFailed: true
            })
          }
        })

    }

    showUpload = () => {
      // Shows the popup for file upload
      this.setState({ showUpload: true });
    }

    hideUpload = () => {
      // Hides the popup for file upload
      this.setState({ showUpload: false });
    }

    renderPopup = () => {
      // Renders the popup with the upload form
      let showHideClassName = null;
      if(this.state.showUpload===true){
        showHideClassName = "popup popup-display-block";
      } else {
        showHideClassName = "popup popup-display-none";  
      }

      let body = null;
      if(this.state.uploadLoading===true){
         body = <Loading />
      } else if(this.state.uploadFailed===true){
        body = (
          <div className='upload-body'>
            <p>
              Error uploading member file.
              Please check the format of the file
            </p>
            <Button
              bsStyle="primary"
              onClick={()=> this.setState({uploadFailed:false})}
            >Try Again</Button>
          </div>
        )
      } else {
        body = (
            <div className='upload-body'>
              <p>
                Upload member data into the dashboard database.
                Accepted file types include .csv files and MS Excel files.
                Columns and data types will be validated prior to uploading.
              </p>
              <Form onSubmit={this.uploadFile}>
                <FormGroup horizontal>
                  <FormControl 
                    className="upload-file"
                    type="file"
                    inputRef={(ref) => this.uploadInput = ref}
                  /><br/>
                  <Button
                    bsStyle="primary"
                    type="submit"
                  >Upload</Button>
                </FormGroup>
              </Form>
            </div>
        )
      }

      return(
        <div className={showHideClassName}>
          <section className="popup-main">
            <h4>Upload Member Data
              <i className="fa fa-times pull-right event-icons"
                 onClick={()=>this.hideUpload()}
              ></i>
            </h4><hr/>
            {body}
          </section>
        </div>
      )
    }

    renderSearch = () => {
      // Renders the serach bar
      return(
        <div className='pull-right'>
          <Form onSubmit={this.handleSearch} inline>
            <FormGroup>
              <FormControl
                className="search-box"
                value={this.state.query}
                onChange={this.handleQuery}
                type="text" 
              />
            </FormGroup>
            <Button 
              className='search-button'
              type="submit"
              data-tip="Returns search results for last name."
            >Search</Button>
            <ReactToolTip />
          </Form>
        </div>
      )
    }

    renderFilter = () => {
      // Renders the filter option
      return(
        <div className='pull-right filter-form'>
          <Form onSubmit={this.handleFilter} inline>
            <FormGroup>
              <Label className='filter-form-label'>Age:</Label>
              <FormControl
                className='filter-form-age-input'
                value={this.state.minAge}
                onChange={this.handleMinAge}
                max={this.state.maxAge}
                type="number" 
              />
            </FormGroup>
            <FormGroup>
              <Label className='filter-form-label'>-</Label>
              <FormControl
                className='filter-form-age-input'
                value={this.state.maxAge}
                onChange={this.handleMaxAge}
                min={this.state.minAge}
                type="number" 
              />
            </FormGroup>
            <Button
              className='search-button'
              type='submit'
              data-tip='Filters the table results.'>Filter</Button>
          </Form>
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
      const popup = this.renderPopup();

      let table = null
      if(this.state.loading){
        table = (
          <div className='event-loading'>
            <Loading/>
          </div>
        )
      } else {
        table = this.renderTable();
      }

      let pageCount = this.renderPageCount();
      let searchTermPills = this.renderSearchTermPills();
      let search = this.renderSearch();
      let filter = this.renderFilter();

      let uploadButton = null
      if(this.state.userRole==='admin'){
        uploadButton = (
            <i 
              className="fa fa-upload pull-right event-icons"
              onClick={()=>this.showUpload()}
              data-tip="Upload member information."
            ></i>
        )
      }

      return (
        <div>
          <Header />
          <div className="Members">
            <div className='events-header'>
              <h2>
                Participants ({this.state.count} total)
                <i className="fa fa-times pull-right event-icons"
                  onClick={()=>this.props.history.push('/')}
                ></i>
                {uploadButton}
              </h2><hr/>
            </div>
            {popup}
            <div className='event-header'>
              {pageCount}
              {search}
              {filter}
            </div>
            <div className='search-term-row pull-right'>
              {searchTermPills.length >0 
                ? <span id='search-term-list'><b>Search Terms:</b></span>
                : null}
              {searchTermPills}
            </div>
            {table}
          </div>
        </div>
      );
    }
}

export default withRouter(Members);
