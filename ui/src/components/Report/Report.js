// Renders the component for the Report screen
import axios from 'axios';
import React, { Component } from 'react';
import { Nav } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import MemberReport from './Tabs/MemberReport';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './Report.css';

class Report extends Component {
  state = {
    activeTab: 'members',
    demographics: [],
    memberLocations: [],
    newMembers: []
  }
  
  componentDidMount(){
    // Checks to make sure the user has access to the 
    refreshAccessToken();
    this.getDemographics();
    this.getMemberLocations();
    this.getNewMembers();
  }

  getDemographics = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/demographics';
    axios.get(url)
      .then(res => {
        this.setState({demographics: res.data});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else if(err.response.status===403){
          this.props.history.push('/forbidden');
        }
      })
  }
  
  getMemberLocations = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/locations';
    axios.get(url)
      .then(res => {
        this.setState({memberLocations: res.data});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else if(err.response.status===403){
          this.props.history.push('/forbidden');
        }
      })
  }
  
  getNewMembers = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/new';
    axios.get(url)
      .then(res => {
        this.setState({newMembers: res.data});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else if(err.response.status===403){
          this.props.history.push('/forbidden');
        }
      })
  }

  switchTab = (tab) => {
    // Toggles between different report tabs
    this.setState({activeTab: tab});
  }

  renderTab = () => {
    // Renders the current displayed tab in the component
    if(this.state.activeTab==='members'){
      return (<MemberReport demographics={this.state.demographics}
                            memberLocations={this.state.memberLocations}/>);
    }
  }

  render() {
    let displayTab = this.renderTab();
    let tabs = null
    let tabStyle = {
      'members': 'record-tab',
      'attendees': 'record-tab',
      'events': 'record-tab'
    }
    const activeTab = this.state.activeTab;
    tabStyle[activeTab] = tabStyle[activeTab] + ' record-tab-selected';

    tabs = (
        <Nav bsStyle="tabs" className="record-tabs">
          <li eventKey="members" 
              className={tabStyle['members']}
              onClick={()=>this.switchTab('members')}>Members</li>
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
          {tabs}
          {displayTab}
        </div>
      </div>
    );
  }
}

export default withRouter(Report);

