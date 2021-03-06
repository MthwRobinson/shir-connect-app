// Renders the component for the Report screen
import axios from 'axios';
import React, { Component } from 'react';
import { Nav } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import MemberReport from './Tabs/MemberReport';
import Header from './../Header/Header';

import './Report.css';

class Report extends Component {
  state = {
    activeTab: 'members',
    // Data for the report tab
    demographics: [],
    memberLocations: {all_members: [], new_members: []},
    newMembers: [],
    newMembersCount: {},
    newMemberDemographics: [],
    householdCount: [],
    resignationCount: [],
    householdType: {all_households: [], new_households: []},
    resignationType: []
  }
  
  componentDidMount(){
    // Checks to make sure the user has access to the 
    refreshAccessToken();
    this.getDemographics();
    this.getMemberLocations();
    this.getNewMembers();
    this.getNewMemberCount();
    this.getNewMemberDemographics();
    this.getHouseholdCount();
    this.getHouseholdType();
    this.getResignationCount();
    this.getResignationType();
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
        } else {
          this.props.history.push('/server-error');
        }
      })
  }
  
  getHouseholdCount = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/households/count?years=25';
    axios.get(url)
      .then(res => {
        this.setState({householdCount: res.data});
      })
  }

  getResignationCount = () => {
    // Counts the number of resignations by year
    let url = '/service/report/members/households/count';
    url += '?years=25&tally=resignations';
    axios.get(url)
      .then(res => {
        this.setState({resignationCount: res.data});
      })
  }
  
  getHouseholdType = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/households/type';
    axios.get(url)
      .then(res => {
        this.setState({householdType: res.data});
      })
  }

  getResignationType = () => {
    // Pulls the resignation reasons for all 
    // resignations that occured within the past year
    const url = '/service/report/members/resignations/type';
    axios.get(url)
      .then(res => {
        this.setState({resignationType: res.data});
      })
  }
  
  getNewMemberDemographics = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/demographics?only=new_members';
    axios.get(url)
      .then(res => {
        this.setState({newMemberDemographics: res.data});
      })
  }
  
  getMemberLocations = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/locations';
    axios.get(url)
      .then(res => {
        this.setState({memberLocations: res.data});
      })
  }
  
  getNewMembers = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/new';
    axios.get(url)
      .then(res => {
        this.setState({newMembers: res.data});
      })
  }
  
  getNewMemberCount = () => {
    // Pulls the current community demographics
    const url = '/service/report/members/new/count';
    axios.get(url)
      .then(res => {
        this.setState({newMemberCount: res.data});
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
                            memberLocations={this.state.memberLocations}
                            newMembers={this.state.newMembers}
                            newMemberCount={this.state.newMemberCount}
                            newMemberDemographics={this.state.newMemberDemographics}
                            householdCount={this.state.householdCount}
                            householdType={this.state.householdType}
                            resignationCount={this.state.resignationCount} 
                            resignationType={this.state.resignationType} />);
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
          {/* <li eventKey="attendees"  */}
          {/*     className={tabStyle['attendees']} */}
          {/*     onClick={()=>this.switchTab('attendees')} */}
          {/* >Attendees</li> */}
          {/* <li eventKey="events" */}
          {/*     className={tabStyle['events']} */}
          {/*     onClick={()=>this.switchTab('events')} */}
          {/* >Events</li> */}
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
