// Renders the component 
import axios from 'axios';
import mapboxgl from 'mapbox-gl';
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import { 
  getMapBoxToken, 
  getDefaultLocation
} from './../../utilities/map';

import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './EventMap.css';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = getMapBoxToken();

class EventMap extends Component {

  constructor(props: Props) {
      super(props);
      this.state = {
        lng: null,
        lat: null,
        zoom: 10.3,
        defaultLocationName: null,
        features: [],
        zipLayer: {},
        mapLoading: true,
        eventsLoading: true,
        events: {
          cities: {},
          counts: {}
        },
        expanded: null,
        map: null
      };
  }

  componentDidMount() {
    this.checkAccess();
    getDefaultLocation()
      .then(res => {
        this.setState({lng: res.data.longitude, lat: res.data.latitude,
                       defaultLocationName: res.data.name})
        const locationPromise = this.getEventLocations();
        const zipPromise = this.getZipCodeGeometries();
        const mapPromise = locationPromise
          // Only build the map after the locations have been loaded
          .then(() =>{
            this.setState({map: this.buildMap()});
          })
        Promise.all([mapPromise, zipPromise])
          .then(() => {
            // First add the zip codes and then add the event
            // locaitons so the event locations will be on top
            this.addAllZipGeometries()
            .then(() => {
              this.addEventLocations();
            })
          })
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

  checkAccess = () => {
    // Checks to make sure the user has access to the 
    // map access group
    const url = '/service/map/authorize';
    let response = axios.get(url)
      .then(res => {
        // Refresh the token to keep the session active
        refreshAccessToken();
      })
      .catch(err => {
        if(err.response.status===403){
          this.props.history.push('/forbidden');
        } else {
          this.props.history.push('/server-error');
        }
      })
    return response

  }

  selectEvent = (eventId) => {
    // Changes to the event page
    const url = '/event?id='+eventId;
    this.props.history.push(url);
  }

  getZipCodeGeometries = () => {
    // Pulls event locations from the database and renders the map
    this.setState({loading: true});
    const url = '/service/map/geometries';
    let response = axios.get(url)
      .then(res => {
        let features = res.data;
        this.setState({zipLayers: features});
      })
    return response
  }
  
  getEventLocations = () => {
    // Pulls event locations from the database and renders the map
    this.setState({loading: true});
    let url = '/service/events/locations';
    if(sessionStorage.getItem('demoMode')==='true'){
      url += '?fake_data=true';
    }
    let response = axios.get(url)
      .then(res => {
        let features = res.data.results;

        const name = this.state.defaultLocationName;
        const DEFAULT_LOCATION = {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [this.state.lng, this.state.lat]
          },
          "properties": {
            "title": name,
            "icon": "religious-jewish",
            "description" : "<strong>" + name + "</strong>"
          }
        }
        features.push(DEFAULT_LOCATION);
        this.setState({features: features, mapLoading: false});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else {
          this.props.history.push('/server-error');
        }
      })
    return response
  }

  addEventLocations = () => {
      // Adds event locations to the map
      this.state.map.addLayer({
          "id": "points",
          "type": "symbol",
          "source": {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": this.state.features 
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

  addAllZipGeometries = () => {
    // Adds map geometries for any zip code
    // with members or events
    const url = '/service/map/zipcodes';
    let response = axios.get(url)
      .then(res => {
        const zipCodes = res.data;
        for(let i=0; i<zipCodes.length; i++){
          const zipCode = parseInt(zipCodes[i], 10);
          if(zipCode in this.state.zipLayers){
            this.addZipGeometry(this.state.map, zipCode);
          }
        }
      })
      .catch(err=>{
        if(err.response.status===401){
          this.history.push('/login');
        } else {
          this.history.push('/server-error');
        }
      })
      return response
  }

  addZipGeometry = (map, zipCode) => {
    // Adds the geometry for a zip code to the map
    const layer = this.state.zipLayers[zipCode];
    map.addLayer(layer);
    map.on('click', layer.id, (e) =>{
      new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(e.features[0].properties.description)
        .addTo(map)
    })
  }

  buildMap = () => {
    // Builds the MapBox GL map
    const { lng, lat, zoom } = this.state;

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
    
    return map
  }

  changeExpanded = (city) => {
    // Changes which list is expanded on the side panel
    if(city===this.state.expanded){
      this.setState({expanded: null});
    } else {
      this.setState({expanded: city});
    }
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
        >
          <div className='legend'>
              <b><span className='legend-title'>Legend</span></b>
              <div><span className='legend-green'></span><b>Balanced</b></div>
              <div><span className='legend-blue'></span><b>More Members</b></div>
              <div><span className='legend-yellow'></span><b>More Events</b></div>
          </div>
        </div>
      )
    }

    return (
      <div>
        <Header />
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
            {mapArea}
          </div>
        </div>
      </div>
    );
  }  

}

export default withRouter(EventMap);
