// Renders the component for the Members screen
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
import moment from 'moment';
import axios from 'axios';

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
        loading: true,
        showUpload: false,
        uploadLoading: false,
        uploadFailed: false
      }

      // Binding for the file upload in the popup
      this.uploadFile = this.uploadFile.bind(this)
      this.handleQuery = this.handleQuery.bind(this)
    }

    componentDidMount(){
      this.getMembers('initial');
    }

    selectMember = (firstName, lastName) => {
      // Switches to the member page
      const url = '/member?firstName='+firstName+'&lastName='+lastName;
      this.props.history.push(url);
    }

    getMembers = (fetchType) => {
      // Pulls members to display in the table
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
      let url = '/service/members?limit='+LIMIT;
      url += '&sort=events_attended&order=DESC';

      // Load settings from session storage
      const memberPage = sessionStorage.getItem('memberPage');
      const memberPages = sessionStorage.getItem('memberPages');
      const memberQuery = sessionStorage.getItem('memberQuery');
      const memberCount = sessionStorage.getItem('memberCount');
      let settingsLoaded = false;
      if(memberPage&&memberPages&&memberCount){
          settingsLoaded = true
      }
      
      // Determine the correct page to load
      if(fetchType==='search'){
        url += '&page=1';
      } else if (fetchType==='up'){
        url += '&page='+(this.state.page+1);
      } else if (fetchType==='down'){
        url += '&page='+(this.state.page-1);
      } else if (fetchType==='initial'&&settingsLoaded){
        url += '&page='+memberPage;
        this.setState({
          page: parseInt(memberPage, 10),
          pages: parseInt(memberPages, 10),
          count: parseInt(memberCount, 10),
          query: memberQuery
        })
      } else {
        url += '&page='+this.state.page;
      }

      // Parse the member query
      if(fetchType==='initial'&&settingsLoaded&&memberQuery){
        if(memberQuery.trim().length>0){
          url += '&q='+memberQuery;
        }
      } else {
        if(this.state.query.trim().length>0){
          url += '&q='+this.state.query;
        }
      }

      axios.get(url, {headers: {Authorization: auth}})
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

          // Save settings in session storage and update state
          sessionStorage.setItem('memberPages', pages);
          sessionStorage.setItem('memberPage', this.state.page);
          sessionStorage.setItem('memberQuery', this.state.query);
          sessionStorage.setItem('memberCount', count);

          this.setState({
            members: members,
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
          this.getMembers('up');
        }
      } else if(direction==='down') {
        if(this.state.page>1){
          const page = this.state.page - 1;
          this.setState({page:page});
          this.getMembers('down');
        }
      }
    }

    handleSubmit = (event) => {
      // Handles the submit action in the search bar
      event.preventDefault();
      this.setState({page: 1});
      this.getMembers('search');
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
      // Creates the table with member information
      return(
        <div>
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>First Name</th>
                  <th className='table-heading'>Last Name</th>
                  <th className='table-heading'>
                    Events
                    <i className='fa fa-caret-down paging-arrows'></i>
                  </th>
                  <th className='table-heading'>Most Recent</th>
                  <th className='table-heading'>Event Name</th>
                </tr>
              </thead>
              <tbody>
                {this.state.members.map((member, index) => {
                  return(
                    <tr 
                      className='table-row' 
                      key={index}
                      onClick={()=>this.selectMember(
                        member.first_name,
                        member.last_name
                      )}
                    >
                      <th>{member.first_name != null
                          ? member.first_name : '--'}</th>
                      <th>{member.last_name != null
                          ? member.last_name : '--'}</th>
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
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
      const url = '/service/members/upload';
      axios.post(url, data, {
          headers: {
            'Authorization': auth,
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

      return (
        <div className="Members">
          <div className='events-header'>
            <h2>
              Participants ({this.state.count})
              <i className="fa fa-times pull-right event-icons"
                 onClick={()=>this.props.history.push('/')}
              ></i>
              <i className="fa fa-upload pull-right event-icons"
                 onClick={()=>this.showUpload()}
              ></i>
            </h2><hr/>
          </div>
          {popup}
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
                  data-tip="Returns search results for last name."
                >Search</Button>
                <ReactToolTip />
              </Form>
            </div>
          </div>
          {table}
        </div>
      );
    }
}

export default withRouter(Members);
