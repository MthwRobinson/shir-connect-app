// Renders the component for individual members
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import moment from 'moment';
import React, { Component } from 'react';
import { Nav } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import { getDefaultLocation } from './../../utilities/map';
import EventHeatmap from './Tabs/EventHeatmap';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';
import MemberEvents from './Tabs/MemberEvents';
import { sortByKey } from './../../utilities/utils';

import './MemberPage.css';


class MemberPage extends Component {
  state = {
    lng: null,
    lat: null,
    loading: true,
    zoom: 10,
    map: null,
    member: {},
    activeTab: 'eventList'
  }

  componentDidMount(){
    getDefaultLocation()
      .then(res => {
        this.setState({lng: res.data.longitude, lat: res.data.latitude});
        this.getMember();
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

  switchTab = (tab) => {
    // Toggles between event info and attendees
    this.setState({activeTab: tab});
  }
  
  sortEvents = (key, ascending=true) => {
    // Sorts events based on the specified key
    // all null values float to the bottom
    //
    // Parameters
    // ----------
    // key: string, the key to sory on
    // ascending: boolean, sorts ascending if true, descending if false
    //
    // Returns
    // -------
    // sorts the array on this.state.event.attendees
    //
    if(this.state.member){
      let member = this.state.member;
      member.events = sortByKey(member.events, key, ascending);
      this.setState({member: member});
    }
  }

  selectEvent = (eventId) => {
    // Switches the page to the event page
    this.props.history.push('/event?id='+eventId);
  }

  getMember = () => {
    this.setState({loading: true});
    const searchTerms = this.props.location.search.split('?')[1].split('&');
    let params = {}
    for(let i=0; i<searchTerms.length; i++){
      const term = searchTerms[i].split('=');
      params[term[0]] = term[1];
    }

    let url = '/service/participant/' + params.id;
    if(sessionStorage.getItem('demoMode')==='true'){
      url += '?fake_data=true';
    }
    axios.get(url)
      .then(res => {
        res.data.name = res.data.first_name 
        res.data.name += ' ' + res.data.last_name;
        this.setState({
          member: res.data,
          loading: false,
        });
        const events = res.data.events;
        for(let i=0; i<events.length; i++){
          const event = events[i];
          if(event.latitude&&event.longitude){
            this.setState({
              lng: event.longitude,
              lat: event.latitude
            })
            break;
          }
        }
        this.setState({map: this.buildMap(events)})
        // Refresh the token to keep the session active
        refreshAccessToken();
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else if(err.response.status===404){
          this.props.history.push('/not-found');
        } else {
          this.props.history.push('/server-error');
        }
      })
  }

  renderMemberInfo = () => {
    if(this.state.member&&this.state.member.events){
        const member = this.state.member;
        let membershipDate = null;
        if(this.state.member.membership_date !== 'None'){
          membershipDate = moment(this.state.member.membership_date)
            .format('MM/DD/YY');
        }

      let events = null;
      if(member.events.length===0){
          events = 'Member has not attended any events.'
      } else {
        if(this.state.activeTab==='heatmap'){
          events = <EventHeatmap member={member} />
        } else if(this.state.activeTab==='eventList'){
          events = <MemberEvents member={member} 
                                 sortEvents={this.sortEvents} />
        }
      }

      let age = null;
      if(member.age){
        age = <li><b>Age:</b> {member.age}</li>
      }
      let joinedDate = null;
      if(membershipDate){
        joinedDate = <li><b>Membership Date:</b> {membershipDate}</li>
      }
      let memberEmail = null;
      if(member.email){
        memberEmail = <li><b>Email: </b> {member.email}</li>
      }
      let info = (
        <ul className='member-info' >
          {age}
          {joinedDate}
          {memberEmail}
        </ul>
      )

      return(
        <div className='event-table'>
          {info}
          <h4><b>Events</b></h4>
          {events}
        </div> 
      )
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
      let features = []
      for(let i=0; i<events.length; i++){
       const event = events[i];
        if(event.latitude&&event.longitude){
            const feature = {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [event.longitude, event.latitude]
              },
              "properties": {
                "title": event.name,
                "icon": "religious-jewish",
              }
            };
            features.push(feature);
          }
      }

      map.addLayer({
          "id": "points",
          "type": "symbol",
          "source": {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": features
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
    })
    
    return map
  }

  render() {
    let memberInfo = this.renderMemberInfo();
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
        'heatmap': 'record-tab',
        'eventList': 'record-tab'
      };
      const activeTab = this.state.activeTab;
      tabStyle[activeTab] = tabStyle[activeTab] + ' record-tab-selected';

      body = (
        <div>
          <div className="MemberPage">
            <div className='events-header'>
              <h2>
                {this.state.member.name}
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
            <Nav bsStyle="tabs" className="record-tabs">
              <li eventKey="eventList"
                  className={tabStyle['eventList']}
                  onClick={()=>this.switchTab('eventList')}
              >Event List</li>
              <li eventKey="heatmap"
                  className={tabStyle['heatmap']}
                  onClick={()=>this.switchTab('heatmap')}
              >Event Heatmap</li>
            </Nav>
            <div className='event-map-container'>
              <div className='event-map-summary-area'>
                {memberInfo}
              </div>
              {mapArea}
            </div>
          </div>
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

export default withRouter(MemberPage);
