import axios from 'axios';
import moment from 'moment';
import React, { Component } from 'react';
import { Nav, Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import {
  getAccessToken,
  refreshAccessToken,
} from './../../utilities/authentication';
import EventInfo from './Tabs/EventInfo';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';
import QuickFacts from './Tabs/QuickFacts';

import './EventPage.css';

class EventPage extends Component {
  state = {
    loading: true,
    event: null,
    activeTab: 'eventInfo'
  }

  componentDidMount(){
    this.getEvent();
    // Refresh the access token to keep the session active
    refreshAccessToken();
  }

  switchTab = (tab) => {
    // Toggles between event info and attendees
    this.setState({activeTab: tab});
  }

  selectMember = (firstName, lastName) => {
    // Switches to the member page
    const url = '/member?firstName='+firstName+'&lastName='+lastName;
    this.props.history.push(url);
  }

  getEvent = () => {
    this.setState({loading: true});
    const token = getAccessToken();
    const auth = 'Bearer '.concat(token)
    const eventId = this.props.location.search.split('=')[1];
    let url = '/service/event/' + eventId;
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        this.setState({
          event: res.data,
          loading: false,
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

  renderAttendees = () => {
    // Renders the list of attendees
    return(
    <div>
        <Row className='event-table'>
          <Table reponsive header hover>
            <thead>
              <tr>
                <th className='table-heading'>First Name</th>
                <th className='table-heading'>
                Last Name
                <i className='fa fa-caret-down paging-arrows'></i>
                </th>
                <th className='table-heading'>E-mail</th>
                <th className='table-heading'>Age</th>
              </tr>
            </thead>
          <tbody>
            {this.state.event.attendees.map((attendee, index) => {
              return(
                <tr 
                  className='table-row' 
                  key={index}
                  onClick={()=>this.selectMember(
                    attendee.first_name,
                    attendee.last_name
                  )}
                >
                  <th>{attendee.first_name != null
                  ? attendee.first_name : '--'}</th>
                  <th>{attendee.last_name != null
                  ? attendee.last_name : '--'}</th>
                  <th>{attendee.email != null
                  ? attendee.email : '--'}</th>
                  <th>{attendee.age != null
                  ? attendee.age : ''}</th>
                </tr>
              )
            })}
          </tbody>
          </Table>
        </Row>
    </div> 
    )
  }

  renderTab = () => {
    if(this.state.event){
      if(this.state.activeTab==='eventInfo'){
        return <EventInfo event={this.state.event} />;
      } else if(this.state.activeTab==='attendees') {
        return this.renderAttendees();
      } else if(this.state.activeTab==='quickFacts'){
        return <QuickFacts event={this.state.event} />;
      }
    } else {
      return(
        <div className='event-loading'>
          <Loading />
        </div>
      )
    }
      
  }

  render() {
    let eventInfo = this.renderTab();
    let body = null;
    
    if(this.state.loading){
      body = (
        <div className='event-loading'>
          <Loading />
        </div>
      )
    } else {
      let tabStyle = {
        'eventInfo': 'record-tab',
        'attendees': 'record-tab',
        'quickFacts': 'record-tab'
      };
      const activeTab = this.state.activeTab;
      tabStyle[activeTab] = tabStyle[activeTab] + ' record-tab-selected';

      body = (
          <div className="EventPage">
            <div className='events-header'>
              <h2>
                {this.state.event.name}
                <i
                  className="fa fa-home pull-right event-icons"
                  onClick={()=>this.props.history.push('/')}
                ></i>
                <i
                  className="fa fa-chevron-left pull-right event-icons"
                  onClick={()=>this.props.history.goBack()}
                ></i>
              </h2><hr/>
            </div>
            <Nav 
              bsStyle="tabs"
              className="record-tabs"
            >
              <li
                eventKey="eventInfo" 
                className={tabStyle['eventInfo']}
                onClick={()=>this.switchTab('eventInfo')}
              >Event Information</li>
              <li 
                eventKey="quickFacts" 
                className={tabStyle['quickFacts']}
                onClick={()=>this.switchTab('quickFacts')}
              >Quick Facts</li>
              <li 
                eventKey="attendees" 
                className={tabStyle['attendees']}
                onClick={()=>this.switchTab('attendees')}
              >Attendees</li>
          </Nav>
          {eventInfo}
          </div>
      )
    }
    return (
      <div>
        <Header />
        {body}
      </div>
    );
  }
}

export default withRouter(EventPage);
