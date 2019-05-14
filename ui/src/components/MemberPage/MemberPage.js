// Renders the component for individual members
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import moment from 'moment';
import React, { Component } from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import { withRouter } from 'react-router-dom';
import ReactTooltip from 'react-tooltip';

import { refreshAccessToken } from './../../utilities/authentication';
import { getDefaultLocation } from './../../utilities/map';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './MemberPage.css';
import 'react-calendar-heatmap/dist/styles.css';


class MemberPage extends Component {
  state = {
    lng: null,
    lat: null,
    loading: true,
    zoom: 10,
    map: null,
    member: {},
    activeTab: 'memberInfo'
  }

  componentDidMount(){
    getDefaultLocation()
      .then(res => {
        this.setState({lng: res.data.longitude, lat: res.data.latitude});
        this.getMember();
      })
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
    const searchTerms = this.props.location.search.split('?')[1].split('&');
    let params = {}
    for(let i=0; i<searchTerms.length; i++){
      const term = searchTerms[i].split('=');
      params[term[0]] = term[1];
    }

    let url = '/service/participant/' + params.id;
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
        } else if(err.response.status===403){
          this.props.history.push('/forbidden');
        }
      })
  }

  renderHeatmap = () => {
      // Renders the calendar heat map
      const member = this.state.member;
      if(member&&member.events){
        
        let values = {};
        for(let i=0; i<member.events.length; i++){
          const event = member.events[i];
          const year = moment(event.start_datetime).format('YYYY');
          const start = moment(event.start_datetime).format('YYYY-MM-DD');
          const value = {
            date: start,
            eventId: event.event_id,
            name: event.name
          }
          if(year in values){
            values[year].push(value);
          } else {
            values[year] = [value];
          }
        }

        return (
          <div>
            <h4><b>Events</b></h4>
            {Object.keys(values).reverse().map((year, index) => {
              const startDate = moment(new Date(year + '-01-01'))
                .add(-1, 'days');
              const endDate = moment(startDate)
                .add(1, 'years')
                .format('YYYY-MM-DD');
              return(
                <div>
                  <h4>{year}</h4>
                  <CalendarHeatmap
                    startDate={startDate}
                    endDate={endDate}
                    values={values[year]}
                    onClick={(value) => this.selectEvent(value.eventId)}

                    tooltipDataAttrs={value => {
                      if(value.name){
                        return {
                          'data-tip': `Attended ${value.name} on ${value.date}`
                        };
                      }
                    }}
                  />
                  <ReactTooltip />
                </div>
              )
            })}
          </div> 
        )
      }
    }

  renderMemberInfo = () => {
    if(this.state.member&&this.state.member.events){
      if(this.state.activeTab==='memberInfo'){
        const member = this.state.member;
        let membershipDate = null;
        if(this.state.member.membership_date !== 'None'){
          membershipDate = moment(this.state.member.membership_date)
            .format('MM/DD/YY');
        }

        let events = null;
        if(member.events.length>0){
          events = this.renderHeatmap();
        } else {
          events = 'Member has not attended any events.'
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
          {events}
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
        'memberInfo': 'record-tab',
        'attendees': 'record-tab'
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
