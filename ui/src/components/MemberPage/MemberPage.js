import React, { Component } from 'react';
import { Nav, Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import moment from 'moment';

import './MemberPage.css';

import Loading from './../Loading/Loading';

class MemberPage extends Component {
  state = {
    lng: -77.173449,
    lat: 38.906103,
    loading: true,
    zoom: 13,
    map: null,
    member: {},
    activeTab: 'memberInfo'
  }

  componentDidMount(){
    this.getMember();
  }

  switchTab = (tab) => {
    // Toggles between event info and attendees
    this.setState({activeTab: tab});
  }

  selectEvent = (eventId) => {
    // Switches the page to the event page
    this.props.history.push('/event?id='+eventId);
  }

  getMember = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    const searchTerms = this.props.location.search.split('?')[1].split('&');
    let params = {}
    for(let i=0; i<searchTerms.length; i++){
      const term = searchTerms[i].split('=');
      params[term[0]] = term[1]
    }

    let url = '/service/member?';
    url += 'firstName=' + params.firstName;
    url += '&lastName=' + params.lastName;
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        res.data.name = res.data.first_name 
        res.data.name += ' ' + res.data.last_name;
        this.setState({
          member: res.data,
          loading: false,
        });
        const events = res.data.events;
        if(events.length>0){
          if(events[0].latitude&&events[0].longitude){
            this.setState({
              lng: events[0].longitude,
              lat: events[0].latitude
            })
          }
        }
        this.setState({map: this.buildMap(events)})
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  renderEventInfo = () => {
    if(this.state.member&&this.state.member.events){
      if(this.state.activeTab==='memberInfo'){
        const member = this.state.member;
        let membershipDate = null;
        if(this.state.member.membership_date != 'None'){
          membershipDate = moment(this.state.member.membership_date)
            .format('MM/DD/YY');
        } else {
          membershipDate = 'None'
        }

      return(
        <div>
          <ul>
            <li><b>Age:</b> {member.age}</li>
            <li>
              <b>Member:</b> {member.is_member == 'True' ? 'Yes' : 'No' }
            </li>
            <li><b>Membership Date: </b> {membershipDate} </li>
            <li><b>Email: </b> {member.email}</li>
            <li><b>Events: </b>
              <ul>
                {member.events.map((event, index) => {
                  const start = moment(event.start_datetime)
                    .format('MM/DD/YY');
                  return(
                    <li
                      className="event-list"
                      onClick={()=>this.selectEvent(event.event_id)}
                    >
                      <b>{start}:</b> {event.name}
                    </li>
                  )
                })}
              </ul>
            </li>
          </ul>
        </div> 
      )
      } else {
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
                    <th className='table-heading'>Member</th>
                  </tr>
                </thead>
              <tbody>
                {this.state.member.attendees.map((attendee, index) => {
                  return(
                    <tr className='table-row' key={index}>
                      <th>{attendee.first_name != null
                      ? attendee.first_name : '--'}</th>
                      <th>{attendee.last_name != null
                      ? attendee.last_name : '--'}</th>
                      <th>{attendee.email != null
                      ? attendee.email : '--'}</th>
                      <th>{attendee.age != null
                      ? attendee.age : '--'}</th>
                      <th>{attendee.is_member === true
                      ? 'Yes' : 'No'}</th>
                    </tr>
                  )
                })}
              </tbody>
              </Table>
            </Row>
        </div> 
        )
      }
    } else {
      return(
        <div className='event-loading'>
          <Loading />
        </div>
      )
    }
      
  }

  buildMap = (events) => {
    // Builds the MapBox GL map
    const { lng, lat, zoom } = this.state;

    const map = new mapboxgl.Map({
      container: this.mapContainer,
      style: 'mapbox://styles/mapbox/streets-v9',
      center: [lng, lat],
      zoom
    });

    map.on('move', () => {
      const { lng, lat } = map.getCenter();

      this.setState({
        lng: lng.toFixed(4),
        lat: lat.toFixed(4),
        zoom: map.getZoom().toFixed(2)
      });
    });

    map.on('load', function() {
      for(let i=0; i<events.length; i++){
        const event = events[i];
        const feature = {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [event.longitude, event.latitude]
          },
          "properties": {
            "title": event.name,
            "icon": "religious-jewish",
            "description" : "<strong>Temple Rodef Shalom</strong>"
          }
        };

        map.addLayer({
            "id": "points",
            "type": "symbol",
            "source": {
              "type": "geojson",
              "data": {
                  "type": "FeatureCollection",
                  "features": [feature]
                }
            },
            "layout": {
                "icon-image": "{icon}-15",
                "text-field": "{title}",
                "text-font": ["Open Sans Semibold", "Open Sans Semibold"],
                "text-offset": [0, 0.6],
                "text-anchor": "top"
            }
        });
      }
    })
    
    return map
  }

  render() {
    let memberInfo = this.renderEventInfo();
    let body = null;
    let mapArea = null;
    if(this.state.mapLoading===true){
      mapArea = (
        <div className='event-map'>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
      )
    } else {
      mapArea = (
        <div 
          ref={el => this.mapContainer = el} 
          className="event-map pull-right"
          id="event-map" 
        />
      )
    }

    if(this.state.loading){
      body = (
        <div className='event-loading'>
          <Loading />
        </div>
      )
    } else {
      let tabStyle = {
        'memberInfo': 'record-tab',
        'attendees': 'record-tab'
      };
      const activeTab = this.state.activeTab;
      tabStyle[activeTab] = tabStyle[activeTab] + ' record-tab-selected';

      body = (
        <div className="MemberPage">
          <div className='events-header'>
            <h2>
              {this.state.member.name}
              <i
                className="fa fa-chevron-left pull-right event-icons"
                onClick={()=>this.props.history.goBack()}
              ></i>
            </h2><hr/>
          </div>
          <div className='event-map-container'>
            <div className='event-map-summary-area'>
              <Nav 
                bsStyle="tabs"
                className="record-tabs"
              >
                <li
                  eventKey="memberInfo" 
                  className={tabStyle['memberInfo']}
                  onClick={()=>this.switchTab('memberInfo')}
                >
                  Member Information
                </li>
                <li 
                  eventKey="attendees" 
                  className={tabStyle['attendees']}
                  onClick={()=>this.switchTab('attendees')}
                >
                  Attendees
                </li>
            </Nav>
              {memberInfo}
            </div>
              {mapArea}
          </div>
        </div>
      )
    }
    return (
      body
    );
  }
}

export default withRouter(MemberPage);
