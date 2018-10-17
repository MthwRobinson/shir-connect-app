// Renders the component for the Members screen
import React, { Component } from 'react';
import {
  Button,
  ControlLabel,
  Form,
  FormControl,
  FormGroup
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import './Members.css';

class Members extends Component {
    constructor(props){
      super(props);
      this.state = {
        showUpload: true
      }
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
              <Form>
                <FormGroup horizontal>
                  <FormControl 
                    className="upload-file"
                    type="file"
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
