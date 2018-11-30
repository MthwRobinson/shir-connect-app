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
    "description" : "<strong>Temple Rodef Shalom</strong>"
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
    this.getEventCounts();
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
  }

  getZipCodeGeometries = () => {
    // Pulls event locations from the database and renders the map
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token);
    const url = '/service/map/geometries';
    let response = axios.get(url, {headers: {Authorization: auth }})
      .then(res => {
        let features = res.data;
        this.setState({zipLayers: features});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
    return response
  }

  getEventCounts = () => {
    // Pulls event counts by location
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token);
    let url = '/service/events/cities';
    let response = axios.get(url, {headers: {Authorization: auth }})
      .then(res => {
        const events = res.data.results;
        this.setState({events: events, eventsLoading: false});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
    return response
  }

  getEventLocations = () => {
    // Pulls event locations from the database and renders the map
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token);
    let url = '/service/events/locations';
    let response = axios.get(url, {headers: {Authorization: auth }})
      .then(res => {
        let features = res.data.results;
        features.push(TRS_LOCATION);
        this.setState({features: features, mapLoading: false});
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
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
    const token = localStorage.getItem('trsToken');
    if(!token){
      this.history.push('/login');
    } else {
      const auth = 'Bearer '.concat(token);
      const url = '/service/map/zipcodes';
      let response = axios.get(url, {headers:{ Authorization: auth}})
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
          }
        })
        return response
    }
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

    //map.on('load', function () {
      // map.addLayer({
      //     "id": "points",
      //     "type": "symbol",
      //     "source": {
      //       "type": "geojson",
      //       "data": {
      //           "type": "FeatureCollection",
      //           "features": features 
      //         }
      //     },
      //     "layout": {
      //         "icon-image": "{icon}-15",
      //         "text-field": "{title}",
      //         "text-font": ["Open Sans Semibold", "Open Sans Semibold"],
      //         "text-offset": [0, 0.6],
      //         "text-anchor": "top"
      //     }
      // });
    //});

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

  renderEventsArea = () => {
    // Renders the section that list events by city
    let eventsArea = null;
    if(this.state.eventsLoading===true){
      eventsArea = <div className='event-loading'><Loading /></div>
    } else {
      // Creates the list of cities to iterate over
      let cities = [];
      for(var city in this.state.events.cities){
        cities.push(city);
      }
      // Creates the list of cities with the number of events in
      // parentheses. If the city is selected, then a sublist
      // of events is also displayed
      eventsArea = (
        <ul className="fa-ul"> 
          {cities.map((city, index) => {
            let expandedList = null
            // The icon will show a plus if the city is expanded
            // and a minus otherwise
            let iconClass = 'bullet-icon fa-li fa';
            if(this.state.expanded===city){
              iconClass += ' fa-minus';
              const cityEvents = this.state.events.cities[city];
              expandedList = (
                <ol className='city-secondary-list'>
                  {cityEvents.map((event, index) => {
                    return(
                      <li>{event.event_name}</li>
                    )
                  })}
                </ol>
              )
            } else {
              iconClass += ' fa-plus';
            }

            return(
              <li 
                className='city-list'
                onClick={()=>this.changeExpanded(city)}
              >
                <i className={iconClass}></i>
                {city} ({this.state.events.counts[city]})
                {expandedList}
              </li>
            )
          })}
        </ul>
      )
    }
    return eventsArea
  }

  render() {
    let eventsArea = this.renderEventsArea();

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
