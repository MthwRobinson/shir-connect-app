import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import moment from 'moment';

import './EventPage.css';

import Loading from './../Loading/Loading';

class EventPage extends Component {
  state = {
    loading: true,
    zoom: 13,
    map: null,
    event: {}
  }

  componentDidMount(){
    this.getEvent();
  }

  getEvent = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    const eventId = this.props.location.search.split('=')[1];
    let url = '/service/event/' + eventId;
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        this.setState({
          event: res.data,
          loading: false,
        });
        let lat = res.data.latitude;
        let long = res.data.longitude;
        let name = res.data.venue_name;
        if(!(lat&&long&&name)){
          long = -77.173449;
          lat = 38.906103;
          name = 'Temple Rodef Shalom';
        }
        this.setState({map: this.buildMap(long, lat, name)})
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  renderEventInfo = () => {
    if(this.state.event){
      const event = this.state.event;
      const start = moment(this.state.event.start_datetime);
      const end = moment(this.state.event.end_datetime);

      let address = '';
      if(event.address_1){
        address += event.address_1;
        if(event.city){
          address += ', ' + event.city;
        }
        if(event.region){
          address += ', ' + event.region;
        }
        if(event.postal_code){
          address += ', ' + event.postal_code;
        }
      }

      return(
        <div>
          <h4><b><u>Event Information</u></b></h4>
          <ul>
            <li><b>Event Link:</b> <a href={event.url}>{event.name}</a></li>
            <li><b>Time: </b> 
              {start.format('MM/DD/YY, h:MM a')}-
              {end.format('MM/DD/YY, h:MM a')}
            </li>
            <li><b>Registered:</b> {event.attendee_count}/{event.capacity} </li>
            <li><b>Venue:</b> {event.venue_name}</li>
            <li><b>Location:</b> {address}</li>
            <li><b>Description:</b> {event.description}</li>

          </ul>
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

  buildMap = (lng, lat, name) => {
    // Builds the MapBox GL map
    const zoom = this.state.zoom;

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
      const feature = {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [lng, lat]
        },
        "properties": {
          "title": name,
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
    })
    
    return map
  }

  render() {
    let eventInfo = this.renderEventInfo();
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
      body = (
        <div className="EventPage">
          <div className='events-header'>
            <h2>
              {this.state.event.name}
              <i
                className="fa fa-times pull-right event-icons"
                onClick={()=>this.props.history.goBack()}
              ></i>
            </h2><hr/>
          </div>
          <div className='event-map-container'>
            <div className='event-map-summary-area'>
              {eventInfo}
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

export default withRouter(EventPage);
