// Renders the component for the Members screen
import React, { Component } from 'react';
import {
  Button,
  Form,
  FormControl,
  FormGroup,
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
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
        showUpload: false
      }

      // Binding for the file upload in the popup
      this.uploadFile = this.uploadFile.bind(this)
      //this.handleQuery = this.handleQuery.bind(this)
    }

    componentDidMount(){
      this.getMembers();
    }

    getMembers = (fetchType) => {
      // Pulls members to display in the table
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
      let url = '/service/members?limit='+LIMIT;
      if(fetchType==='search'){
        url += '&page=1';
      } else if (fetchType==='up'){
        url += '&page='+(this.state.page+1);
      } else if (fetchType==='down'){
        url += '&page='+(this.state.page-1);
      } else {
        url += '&page='+this.state.page;
      }
      if(this.state.query.trim().length>0){
        url += '&q='+this.state.query;
      }
      axios.get(url, {headers: {Authorization: auth}})
        .then(res => {
          let members = [];
          for(var i=0; i<res.data.results.length; i++){
            let member = res.data.results[i];
            var birthday = moment(member.birth_date);
            member.birth_date = birthday.format('MM/DD/YY');
            var membership_date = moment(member.membership_date);
            member.membership_date = membership_date.format('MM/DD/YY');
            members.push(member);
          }
          
          this.setState({
            members: members,
            count: parseInt(res.data.count, 10),
            pages: parseInt(res.data.pages, 10),
            loading: false
          });
          console.log(this.state.members);
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
    }

    uploadFile(event) {
      // Handles uploading the member data in the popup
      event.preventDefault();

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
          this.hideUpload();    
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
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

      return(
        <div className={showHideClassName}>
          <section className="popup-main">
            <h4>Upload Member Data
              <i className="fa fa-times pull-right event-icons"
                 onClick={()=>this.hideUpload()}
              ></i>
            </h4><hr/>
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
          </section>
        </div>
      )
    }
  

    render() {
      const popup = this.renderPopup();

      return (
        <div className="Members">
          <div className='events-header'>
            <h2>
              Members
              <i className="fa fa-times pull-right event-icons"
                 onClick={()=>this.props.history.push('/')}
              ></i>
              <i className="fa fa-upload pull-right event-icons"
                 onClick={()=>this.showUpload()}
              ></i>
            </h2><hr/>
          </div>
          {popup}
        </div>
      );
    }
}

export default withRouter(Members);
