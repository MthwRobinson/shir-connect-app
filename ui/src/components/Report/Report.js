// Renders the component for the Report screen
import axios from 'axios';
import React, { Component } from 'react';
import { Nav } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Report.css';

class Report extends Component {
  state = {
    loading: false,
    activeTab: 'attendees'
  }
  
  componentDidMount(){
    // Checks to make sure the user has access to the 
    refreshAccessToken();
  }

  switchTab = (tab) => {
    // Toggles between different report tabs
    this.setState({activeTab: tab});
  }

  render() {
    let body = null
    if(this.state.loading){
      body = (<div className="event-loading"><Loading /></div>)
    } else {
      let tabStyle = {
        'report': 'record-tab',
        'attendees': 'record-tab',
        'events': 'record-tab'
      }
      const activeTab = this.state.activeTab;
      tabStyle[activeTab] = tabStyle[activeTab] + ' record-tab-selected';

      body = (
          <Nav bsStyle="tabs" className="record-tabs">
            <li eventKey="report" 
                className={tabStyle['report']}
                onClick={()=>this.switchTab('report')}>Report</li>
            <li eventKey="attendees" 
                className={tabStyle['attendees']}
                onClick={()=>this.switchTab('attendees')}
            >Attendees</li>
            <li eventKey="events"
                className={tabStyle['events']}
                onClick={()=>this.switchTab('events')}
            >Events</li>
          </Nav>
      )
    }

    return (
      <div>
        <Header />
        <div className="Report">
          <div className='events-header'>
            <h2>Report
              <i
                className="fa fa-times pull-right event-icons"
                onClick={()=>this.props.history.push('/')}
              />
            </h2><hr/>
          </div>
          {body}
        </div>
      </div>
    );
  }
}

export default withRouter(Report);

