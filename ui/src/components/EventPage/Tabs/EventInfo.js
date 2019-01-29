import mapboxgl from 'mapbox-gl';
import moment from 'moment';
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import { getMapBoxToken } from './../../../utilities/authentication';

mapboxgl.accessToken = getMapBoxToken();

class EventInfo extends Component {
  state = {
    zoom: 13,
    map: null
  }

  componentDidMount(){
    if(this.props.event){
      let lat = this.props.event.latitude;
      let long = this.props.event.longitude;
      let name = this.props.event.venue_name;
      if(!(lat&&long&&name)){
        long = -77.173449;
        lat = 38.906103;
        name = 'Temple Rodef Shalom';
      }
      this.setState({map: this.buildMap(long, lat, name)})
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

  render(){
    // Render the map area to the right of the screen 
    let mapArea = (
      <div 
        ref={el => this.mapContainer = el} 
        className="event-map pull-right"
        id="event-map" 
      />
    )

    // Render the event information on the left
    const event = this.props.event;
    const start = moment(event.start_datetime);
    const end = moment(event.end_datetime);

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

    let attendeeCount = 0;
    if(event.attendee_count > 0){
      attendeeCount = event.attendee_count;
    }

    return(
      <div className='event-map-container'>
        <div className='event-map-summary-area'>
          <div className='event-table'>
            <ul>
              <li><b>Event Link:</b> <a href={event.url}>{event.name}</a></li>
              <li><b>Time: </b> 
                {start.format('MM/DD/YY, h:MM a')}{' - '}
                {end.format('MM/DD/YY, h:MM a')}
              </li>
              <li><b>Attendees: {event.attendee_count}</b></li>
              <li><b>Average Cost: </b>
                ${(event.total_fees/event.attendee_count).toFixed(2)}
              </li>
              <li><b>Venue:</b> {event.venue_name != null
                  ? event.venue_name : 'Temple Rodef Shalom'}
              </li>
              <li><b>Location:</b> {address.length>0
                  ? address : 'Not Available'}
              </li>
              <li><b>Description:</b> {event.description}</li>
            </ul>
          </div>
        </div>
          {mapArea}
      </div>
    )
  }
};
export default withRouter(EventInfo);
