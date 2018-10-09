import React, { Component } from 'react';
import mapboxgl from 'mapbox-gl';
import axios from 'axios';
import { withRouter } from 'react-router-dom';

import Loading from './../Loading/Loading';

import './EventMap.css';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'pk.eyJ1IjoibXRod3JvYmluc29uIiwiYSI6ImNqNXUxcXcwaTAyamcyd3J4NzBoN283b3AifQ.JIfgHM7LDVb34sWhN4L8aA';

const TRS_LOCATION = {
  "type": "Feature",
  "geometry": {
            "type": "Point",
            "coordinates": [-77.173449, 38.906103]
        },
  "properties": {
            "title": "Temple Rodef Shalom",
            "icon": "religious-jewish",
    "description" : "<strong>Temple Rodef Shalom</strong><p>hi</p>"
    }
}

class EventMap extends Component {

  constructor(props: Props) {
      super(props);
      this.state = {
        lng: -77.174,
        lat: 38.906,
        zoom: 10.3,
        features: [],
        mapLoading: true,
        eventsLoading: true
      };
  }

  componentDidMount() {
    this.getEventLocations();
  }

  getEventLocations = () => {
    // Pulls event locations from the database and renders the map
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token);
    let url = '/service/events/locations';
    axios.get(url, {headers: {Authorization: auth }})
      .then(res => {
        let features = res.data.results;
        features.push(TRS_LOCATION);
        this.setState({features: features, mapLoading: false});
        this.buildMap()
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })

  }

  buildMap = () => {
    // Builds the MapBox GL map
    const { lng, lat, zoom, features } = this.state;

    var popup = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false
    });

    const map = new mapboxgl.Map({
      container: this.mapContainer,
      style: 'mapbox://styles/mapbox/light-v9',
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

    map.on('mouseenter', 'points', function(e) {
        // Change the cursor style as a UI indicator.
        map.getCanvas().style.cursor = 'pointer';

        var coordinates = e.features[0].geometry.coordinates.slice();
        var description = e.features[0].properties.description;

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        // Populate the popup and set its coordinates
        // based on the feature found.
        popup.setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
    });

    map.on('mouseleave', 'points', function() {
        map.getCanvas().style.cursor = '';
        popup.remove();
    });    


    map.on('load', function () {

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
    });
  }

  render() {

    let mapArea = null;
    if(this.state.mapLoading===true){
      mapArea = (
        <div className='map'>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
      )
    } else {
      mapArea = (
        <div 
          ref={el => this.mapContainer = el} 
          className="map pull-right"
          id="map" 
        />
      )
    }

    let eventsArea = null;
    if(this.state.eventsLoading===true){
      eventsArea = <div className='event-loading'><Loading /></div>
    } else {
      eventsArea = null
    }

    return (
      <div className="EventMap">
        <div className='events-header'>
          <h2>
            Event Map
            <i
              className="fa fa-times pull-right event-icons"
              onClick={()=>this.props.history.push('/')}
            ></i>
          </h2><hr/>
        </div>
        <div className='map-container'>
          <div className='map-summary-area'>
            <h4>Events by City</h4><hr/>
            {eventsArea}
          </div>
          {mapArea}
        </div>
      </div>
    );
  }  

}

export default withRouter(EventMap);
