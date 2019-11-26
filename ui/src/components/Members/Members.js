// Renders the component for the Members screen
import axios from 'axios';
import moment from 'moment';
import React, { Component } from 'react';
import {
  Button,
  ControlLabel,
  Form,
  FormControl,
  FormGroup,
  Label,
  Row,
  Table
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import ReactTooltip from 'react-tooltip';
import Swipe from 'react-easy-swipe';
import Modal from 'react-responsive-modal';

import {
  getCSRFToken,
  refreshAccessToken
} from './../../utilities/authentication';
import { getConfigName } from './../../utilities/utils';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Members.css';

const LIMIT = 25;
const CONFIG_NAME = getConfigName();
const COLUMNS = require('./config.json');

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
        maxAge: null,
        fileType: 'members',
        showFilter: false
      }

      // Binding for the file upload in the popup
      this.uploadFile = this.uploadFile.bind(this);
      this.handleQuery = this.handleQuery.bind(this);
      this.handleMinAge = this.handleMinAge.bind(this);
      this.handleMaxAge= this.handleMaxAge.bind(this);
      this.handleFileType = this.handleFileType.bind(this);
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
          } else {
            this.props.history.push('/server-error');
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
      if(sessionStorage.getItem('demoMode')==='true'){
        url += '&fake_data=true';
      }
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
      this.hideFilter();
    }

    clearFilter = () => {
        // Clears the filters for participants
        this.setState({
          minAge: null,
          maxAge: null,
          showFilter: false
        })
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

    handleFileType(event){
      // Updates the file type
      this.setState({ fileType: event.target.value });
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

    buildTableColumns = () => {
      // Builds the list of columns that are available for the client
      let sortArrow = this.state.sortOrder === 'desc' ? 'down' : 'up';
      const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';
      let columns = [];
      if(CONFIG_NAME in COLUMNS){
        columns = COLUMNS[CONFIG_NAME] ;
      } else {
        columns = COLUMNS["default"] ;
      }

      let tableColumns = [];
      for(let column of columns){
        tableColumns.push(
          <th className='table-heading'
              onClick={()=>this.handleSort(column.column)}>
            {column.text}
            {this.state.sortColumn === column.column
            ? <i className={arrowClass}></i>
            : null}
          </th>
        )
      }
      return tableColumns ;
    }

    buildMemberRow = (member) => {
      // Construct the appropriate table row entry for the member
      let columns = [];
      if(CONFIG_NAME in COLUMNS){
        columns = COLUMNS[CONFIG_NAME] ;
      } else {
        columns = COLUMNS["default"] ;
      }

      const memberRow = [];
      for(let column of columns){
        let row = null;
        if(column.column === "is_member"){
          row = <th>{member.is_member === true? 'Y' : 'N'}</th>
        } else {
          row = <th>{member[column.column] != null ? member[column.column] : '--'}</th>
        }
        memberRow.push(row);
      }
      return memberRow ;
    }

    renderTable = () => {
      // Creates the table with member information
      const tableColumns = this.buildTableColumns();
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
                    {tableColumns}
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
                        {this.buildMemberRow(member)}
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
      const url = '/service/members/upload?file_type=' + this.state.fileType;
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

    showFilter = () => {
      // Toggles the filter modal
      this.setState({ showFilter: true});
    }

    hideFilter = () => {
      // Toggles the filter modal
      this.setState({ showFilter: false });
    }

    renderPopup = () => {
      // Renders the popup with the upload form
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
                <FormGroup>
                  <ControlLabel>File Type</ControlLabel>
                  <FormControl componentClass="select"
                               value={this.state.fileType}
                               onChange={this.handleFileType}>
                    <option value="members">Members</option>
                    <option value="resignations">Resignations</option>
                  </FormControl>
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
        <div>
          <Modal
            open={this.state.showUpload}
            showCloseIcon={false}
            center
          >
            <h4>Upload Member Data
              <i className="fa fa-times pull-right event-icons"
                 onClick={()=>this.hideUpload()}
              ></i>
            </h4><hr/>
            {body}
          </Modal>
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
              bsStyle="primary"
              type="submit"
              data-tip="Returns search results for last name."
            >Search</Button>
          </Form>
        </div>
      )
    }

    renderFilter = () => {
      // Renders the filter option
      return(
        <Modal
          open={this.state.showFilter}
          showCloseIcon={false}
          center
        >
          <h4>Filter
            <i className="fa fa-times pull-right event-icons"
                onClick={()=>this.hideFilter()}
            ></i>
          </h4><hr/>
          <Form onSubmit={this.handleFilter} >
              <FormGroup>
                <Label>Minimum Age:</Label>
                <FormControl
                  value={this.state.minAge}
                  onChange={this.handleMinAge}
                  max={this.state.maxAge}
                  type="number"
                />
              </FormGroup>
              <FormGroup>
                <Label>Maximum Age:</Label>
                <FormControl
                  value={this.state.maxAge}
                  onChange={this.handleMaxAge}
                  min={this.state.minAge}
                  type="number"
                />
              </FormGroup>
              <Button
                className='search-button'
                bsStyle="primary"
                type='submit'>Apply Filter</Button>
              <Button
                className='search-button'
                bsStyle="danger"
                onClick={()=>this.clearFilter()}>Clear Filter</Button>
          </Form>
        </Modal>
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
      const filter = this.renderFilter();

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

      let uploadButton = 'hidden'
      if(this.state.userRole==='admin'){
        uploadButton = ''
      }
      let info = "There are " + String(this.state.count) + " total participants. <br/>";
      info += "Click or tap on an event for more information. <br/>";
      info += "On tablet, swipe right or left to switch pages."

      return (
        <div>
          <Header />
          <div className="Members">
            <div className='events-header'>
              <h2>
                Participants{' '}
                <sup><i className='fa fa-info-circle'
                        data-tip={info}></i>
                </sup>
                <i className="fa fa-times pull-right event-icons"
                  onClick={()=>this.props.history.push('/')}
                ></i>
                <i className="fa fa-filter pull-right event-icons"
                  data-tip="Add a filter to the table."
                  onClick={()=>this.showFilter()}
                ></i>
                <i className={"fa fa-upload pull-right event-icons " + uploadButton}
                    onClick={()=>this.showUpload()}
                    data-tip="Upload member information."></i>
              </h2><hr/>
            </div>
            {popup}
            {filter}
            <div className='event-header'>
              {pageCount}
              {search}
            </div>
            <div className='search-term-row pull-right'>
              {searchTermPills.length >0
                ? <span id='search-term-list'><b>Search Terms:</b></span>
                : null}
              {searchTermPills}
            </div>
            {table}
          </div>
          <ReactTooltip html={true} />
        </div>
      );
    }
}

export default withRouter(Members);
