import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import './EventPage.css';

import Loading from './../Loading/Loading';

class EventPage extends Component {
  state = {
    loading: true,
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
          loading: false
        });
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  render() {
    let body = null;
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
        </div>
      )
    }
    return (
      body
    );
  }
}

export default withRouter(EventPage);
